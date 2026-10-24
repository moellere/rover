"""
Overhead-closed steering: face a heading, or drive to a point, using the
bench camera's view of the marker on Grover's top (`overhead.py`) as the
truth and the ESP32's gyro turn as the actuator for heading.

Frame: the overhead image's. Angles 0 = image right, 90 = image up (CCW
+). Positions in pixels of the bench camera; distances converted with the
marker's local mm/px (approximate - the lens is wide, so the scale at the
target can differ from the scale at Grover; the loop re-measures every
step, so the error only sizes the next pulse).

`face(heading)`   locate -> gyro turn by the error -> locate, until the
                  overhead reads within `tol` (the gyro's scale is
                  calibrated against this same camera, 2026-10-24, so one
                  turn normally does it).
`go_to(target)`   repeat: locate (settled: two overhead frames that agree,
                  the camera lags the world by up to ~2.5 s); bearing and
                  distance to the target; if
                  the heading error is large, face the target; else a
                  forward pulse sized from the distance and the measured
                  speed (learned from the previous pulse); stop inside
                  `stop_mm`. Pivots walk a tank a few cm, so re-locate
                  after every action rather than dead-reckon.

The firmware's guards (TFMini obstacle stop, cliff, battery, watchdog)
stay authoritative underneath; this loop also refuses to start on a low
battery or an active cliff sensor, like `drive`. Check the lane on the
overhead before a run (CLAUDE.md: the TFMini only sees straight ahead).
"""
import asyncio
import math
import time
from dataclasses import dataclass, field

from brain.cameras import snapshot
from brain.overhead import Pose, ROVER_TOP_ID, heading_change, poses
from brain.rover_client import RoverClient

LOW_BATTERY_V = 9.6
FACE_TOL_DEG = 3.0
FACE_MAX_TURNS = 3
MIN_TURN_DEG = 2.0          # below the gyro's lead/noise; don't bother
GO_HEADING_TOL = 10.0       # re-face when the bearing error exceeds this
FIRST_PULSE_S = 0.3
MAX_PULSE_S = 1.0
MIN_PULSE_S = 0.15
FAST_MM_S = 700.0           # size pulses as if the tank were this fast unless it has proven faster:
                            # the first pulse after a pivot is stiction-slow (14 cm/s on 10-24) and
                            # sizing the next one from it ran 70 cm in one pulse
PULSE_FRACTION = 0.7        # aim each pulse at this fraction of the remaining distance
MAX_LOST = 3


@dataclass
class SteerResult:
    ok: bool
    reason: str
    steps: int
    pose: dict | None
    log: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"ok": self.ok, "reason": self.reason, "steps": self.steps, "pose": self.pose, "log": self.log}


SETTLE_TIMEOUT_S = 5.0      # overhead frames arrive up to ~2.5 s stale after motion (measured 10-24)
SETTLE_PX = 3.0
SETTLE_DEG = 1.5


def _rover(camera: str, settle: bool = True) -> tuple[Pose | None, list[Pose]]:
    """Grover's pose from the overhead. With `settle`, keep taking frames until
    two in a row agree (the camera's snapshot runs a couple of seconds behind
    the world, so the first frame after a move still shows it moving)."""
    found = poses(snapshot(camera))
    rover = next((p for p in found if p.id == ROVER_TOP_ID), None)
    if not settle:
        return rover, found
    t0 = time.monotonic()
    while time.monotonic() - t0 < SETTLE_TIMEOUT_S:
        found2 = poses(snapshot(camera))
        rover2 = next((p for p in found2 if p.id == ROVER_TOP_ID), None)
        if rover is not None and rover2 is not None and \
           math.hypot(rover.x_px - rover2.x_px, rover.y_px - rover2.y_px) <= SETTLE_PX and \
           abs(heading_change(rover.heading_deg, rover2.heading_deg)) <= SETTLE_DEG:
            return rover2, found2
        rover, found = rover2, found2
    return rover, found


def _pose_dict(p: Pose | None) -> dict | None:
    return None if p is None else {"x_px": round(p.x_px, 1), "y_px": round(p.y_px, 1),
                                   "heading_deg": p.heading_deg, "mm_per_px": p.mm_per_px}


async def _preflight(client: RoverClient) -> str | None:
    st = await client.state(timeout=3.0)
    if st.battery_voltage is not None and st.battery_voltage < LOW_BATTERY_V:
        return f"battery {st.battery_voltage:.2f}V below {LOW_BATTERY_V}V"
    if st.front_left_cliff or st.front_right_cliff:
        return "cliff sensor active"
    if st.yaw_deg is None:
        return "gyro not reporting"
    return None


async def face(heading_deg: float, camera: str = "bench", tol: float = FACE_TOL_DEG,
               max_turns: int = FACE_MAX_TURNS, duty: int = 0) -> SteerResult:
    client = RoverClient()
    bad = await _preflight(client)
    if bad:
        return SteerResult(False, bad, 0, None)
    log: list = []
    rover, _ = _rover(camera)
    for i in range(max_turns + 1):
        if rover is None:
            return SteerResult(False, "rover marker not seen", i, None, log)
        err = heading_change(rover.heading_deg, heading_deg)
        log.append({"heading": rover.heading_deg, "error": round(err, 1)})
        if abs(err) <= tol:
            return SteerResult(True, f"facing {rover.heading_deg} (goal {heading_deg})", i, _pose_dict(rover), log)
        if i == max_turns:
            break
        if abs(err) >= MIN_TURN_DEG:
            await client.turn(err, duty)
            await asyncio.sleep(0.5)
        rover, _ = _rover(camera)
    return SteerResult(False, f"still {err:+.1f} deg off after {max_turns} turns", max_turns, _pose_dict(rover), log)


async def go_to(x_px: float | None = None, y_px: float | None = None, marker_id: int | None = None,
                stop_mm: float = 150.0, camera: str = "bench", max_steps: int = 10) -> SteerResult:
    """Drive to a pixel target, or to another marker's position (`marker_id`,
    e.g. id 0 lying flat on the bench as the goal spot)."""
    client = RoverClient()
    bad = await _preflight(client)
    if bad:
        return SteerResult(False, bad, 0, None)
    log: list = []
    speed = FAST_MM_S
    lost = 0
    prev: tuple[Pose, float, float] | None = None   # pose before the last pulse, pulse s, mm/px
    t0 = time.monotonic()
    for step in range(max_steps):
        rover, found = _rover(camera)
        if rover is None:
            lost += 1
            if lost >= MAX_LOST:
                return SteerResult(False, f"rover marker lost {MAX_LOST} frames", step, None, log)
            await asyncio.sleep(0.5)
            continue
        lost = 0
        if marker_id is not None:
            tgt = next((p for p in found if p.id == marker_id), None)
            if tgt is None:
                return SteerResult(False, f"target marker {marker_id} not seen", step, _pose_dict(rover), log)
            tx, ty = tgt.x_px, tgt.y_px
            scale = (rover.mm_per_px + (tgt.mm_per_px or rover.mm_per_px)) / 2
        else:
            if x_px is None or y_px is None:
                return SteerResult(False, "need x_px and y_px, or marker_id", step, _pose_dict(rover), log)
            tx, ty, scale = x_px, y_px, rover.mm_per_px
        if prev is not None:
            moved_mm = math.hypot(rover.x_px - prev[0].x_px, rover.y_px - prev[0].y_px) * prev[2]
            if prev[1] > 0 and moved_mm > 20:
                speed = max(FAST_MM_S, min(1200.0, moved_mm / prev[1]))   # only ever assume faster
            prev = None
        dx, dy = tx - rover.x_px, -(ty - rover.y_px)
        dist_mm = math.hypot(dx, dy) * scale
        bearing = math.degrees(math.atan2(dy, dx)) % 360
        err = heading_change(rover.heading_deg, bearing)
        entry = {"t": round(time.monotonic() - t0, 1), "x": round(rover.x_px), "y": round(rover.y_px),
                 "heading": rover.heading_deg, "bearing": round(bearing, 1), "error": round(err, 1),
                 "dist_mm": round(dist_mm)}
        if dist_mm <= stop_mm:
            log.append({**entry, "action": "arrived"})
            return SteerResult(True, f"arrived: {dist_mm:.0f} mm from target", step, _pose_dict(rover), log)
        if abs(err) > GO_HEADING_TOL:
            log.append({**entry, "action": f"turn {err:+.0f}"})
            await client.turn(err, 0)
            await asyncio.sleep(0.5)
            continue
        pulse = max(MIN_PULSE_S, min(MAX_PULSE_S, (dist_mm - stop_mm * 0.5) * PULSE_FRACTION / speed))
        log.append({**entry, "action": f"forward {pulse:.2f}s", "speed_mm_s": round(speed)})
        st = await client.state(timeout=3.0)
        if st.front_left_cliff or st.front_right_cliff:
            return SteerResult(False, "cliff sensor active", step, _pose_dict(rover), log)
        await client.drive("forward", pulse)
        prev = (rover, pulse, scale)
        await asyncio.sleep(0.3)
    rover, _ = _rover(camera)
    return SteerResult(False, f"step cap {max_steps} reached", max_steps, _pose_dict(rover), log)


GOAL_CLEAR_MM = 450.0       # overhead leg stops here: Grover's nose then sits short of the goal
                            # sheet (printer paper under a scrubbing track stalls pivots, 10-24)


async def dock_approach(goal_marker: int = 0, final_marker: int = 1, final_stop_mm: float = 120.0,
                        camera: str = "bench", max_steps: int = 10, max_pulses: int = 12) -> dict:
    """The two halves chained: `go_to` the goal-spot marker on the overhead
    (stopping GOAL_CLEAR_MM out, nose toward it), then hand over to the
    onboard camera's `home_to_marker` for the upright marker behind it."""
    from brain.homing import home_to_marker
    leg1 = await go_to(marker_id=goal_marker, stop_mm=GOAL_CLEAR_MM, camera=camera, max_steps=max_steps)
    out = {"overhead": leg1.as_dict()}
    if not leg1.ok:
        out.update(ok=False, reason=f"overhead leg: {leg1.reason}")
        return out
    leg2 = await home_to_marker(final_marker, "rover", final_stop_mm, max_pulses)
    out["onboard"] = leg2.__dict__ if hasattr(leg2, "__dict__") else leg2
    out.update(ok=leg2.ok, reason=f"onboard leg: {leg2.reason}")
    return out
