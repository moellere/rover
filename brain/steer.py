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


POST_MOVE_S = 2.5           # overhead frames arrive up to ~2.5 s stale after motion (measured 10-24)
SETTLE_GAP_S = 1.0          # frames compared for agreement are this far apart (the camera can
                            # serve the same stale frame twice in a row, 10-24 run 2)
SETTLE_TIMEOUT_S = 6.0
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
        time.sleep(SETTLE_GAP_S)
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
            await asyncio.sleep(POST_MOVE_S)
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
            await asyncio.sleep(POST_MOVE_S)
            continue
        pulse = max(MIN_PULSE_S, min(MAX_PULSE_S, (dist_mm - stop_mm * 0.5) * PULSE_FRACTION / speed))
        log.append({**entry, "action": f"forward {pulse:.2f}s", "speed_mm_s": round(speed)})
        st = await client.state(timeout=3.0)
        if st.front_left_cliff or st.front_right_cliff:
            return SteerResult(False, "cliff sensor active", step, _pose_dict(rover), log)
        await client.drive("forward", pulse)
        prev = (rover, pulse, scale)
        await asyncio.sleep(POST_MOVE_S)
    rover, _ = _rover(camera)
    return SteerResult(False, f"step cap {max_steps} reached", max_steps, _pose_dict(rover), log)


GOAL_CLEAR_MM = 450.0       # overhead leg stops here: Grover's nose then sits short of the goal
                            # sheet (printer paper under a scrubbing track stalls pivots, 10-24)


async def dock_approach(goal_marker: int | None = 0, final_marker: int = 1, final_stop_mm: float = 120.0,
                        camera: str = "bench", max_steps: int = 10, max_pulses: int = 12,
                        goal_x_px: float | None = None, goal_y_px: float | None = None,
                        goal_clear_mm: float = GOAL_CLEAR_MM) -> dict:
    """The two halves chained: `go_to` the goal spot on the overhead - a flat
    marker, or a pixel (`goal_x_px`, `goal_y_px`, e.g. the dock's position
    when its tower hides the upright marker) - stopping `goal_clear_mm` out,
    nose toward it, then hand over to the onboard camera's `home_to_marker`
    for the upright marker (`final_marker`, id 3 at 50 mm on the dock tower)."""
    from brain.homing import home_to_marker
    if goal_x_px is not None and goal_y_px is not None:
        leg1 = await go_to(x_px=goal_x_px, y_px=goal_y_px, stop_mm=goal_clear_mm, camera=camera, max_steps=max_steps)
    else:
        leg1 = await go_to(marker_id=goal_marker, stop_mm=goal_clear_mm, camera=camera, max_steps=max_steps)
    out = {"overhead": leg1.as_dict()}
    if not leg1.ok:
        out.update(ok=False, reason=f"overhead leg: {leg1.reason}")
        return out
    leg2 = await home_to_marker(final_marker, "rover", final_stop_mm, max_pulses)
    out["onboard"] = leg2.__dict__ if hasattr(leg2, "__dict__") else leg2
    out.update(ok=leg2.ok, reason=f"onboard leg: {leg2.reason}")
    return out


# ---- Docking on the overhead alone (2026-10-24) ---------------------------
# The onboard camera aims at the dock marker but cannot align to the dock's
# axis, and looks over the 65 mm tower once close. The overhead sees Grover's
# marker at ~1.4 mm/px at the dock, which is finer than the rollers need
# (+/-9 mm fore-aft, +/-5 lateral). So: a taught docked pose (brain/
# dock_pose.json, Enoch pushes Grover fully on by hand once), waypoints on
# the dock's axis behind it, square up with `face`, creep in with the
# obstacle guard relaxed until the overhead says the pose is reached or
# Grover stops moving (the tower).
import json
from pathlib import Path

DOCK_POSE_FILE = Path(__file__).with_name("dock_pose.json")
DOCK_WAYPOINTS_MM = (450.0, 200.0)   # on the axis, behind the docked pose
DOCK_ARRIVE_MM = 0.0        # creep until AT the taught pose: 6 mm short had no contact (2026-10-26)
DOCK_CREEP_S = 0.12
DOCK_MAX_CREEPS = 14
DOCK_STALL_PX = 4.0
DOCK_BUMP_MM = 25.0         # a stall this close to the pose = bumper against the wall
DOCK_CHARGE_WAIT_S = 30.0   # battery_voltage is a 25 s rolling average
DOCK_CHARGE_STEP_V = 0.15   # resting ~11.8 V -> ~12.0-12.2 V on the dock
DOCK_GUARD_OFF_MM = 250.0  # waypoints this close relax the obstacle guard (the tower is in range)
DOCK_LATERAL_MM = 8.0       # creep steers back onto the axis beyond this (the rollers allow ~+/-5)
DOCK_LOOKAHEAD_MM = 100.0   # ... aiming at the axis this far ahead of Grover


def load_dock_pose() -> dict:
    return json.loads(DOCK_POSE_FILE.read_text())


def _axis_point(pose: dict, back_mm: float) -> tuple[float, float]:
    """A point `back_mm` behind the docked pose along its heading (image frame, y down)."""
    h = math.radians(pose["heading_deg"])
    px = back_mm / pose["mm_per_px"]
    return pose["x_px"] - math.cos(h) * px, pose["y_px"] + math.sin(h) * px


async def dock(camera: str = "bench", max_steps: int = 8) -> dict:
    pose = load_dock_pose()
    client = RoverClient()
    bad = await _preflight(client)
    if bad:
        return {"ok": False, "reason": bad}
    log: list = []
    st = await client.state(timeout=3.0)
    guard = st.obstacle_stop_cm or 0.0
    v_before = st.battery_voltage
    try:
        r = await _dock_legs(client, pose, camera, max_steps, log, guard)
        if r.get("ok"):
            # on the pose (or stalled against the bumper): confirm by the voltage step.
            # battery_voltage is a 25 s rolling average, so wait it out.
            await asyncio.sleep(DOCK_CHARGE_WAIT_S)
            st = await client.state(timeout=3.0)
            v_after = st.battery_voltage
            charging = (v_before is not None and v_after is not None
                        and v_after - v_before >= DOCK_CHARGE_STEP_V)
            r["charging"] = charging
            r["volts"] = {"before": v_before, "after": v_after}
            r["reason"] += (f"; charging ({v_before:.2f} -> {v_after:.2f} V)" if charging
                            else f"; NOT charging ({v_before} -> {v_after} V) - contacts missed")
        return r
    finally:
        if guard > 0:
            try:
                await client.set_number("obstacle_stop", guard)
            except Exception:
                pass


async def _dock_legs(client: RoverClient, pose: dict, camera: str, max_steps: int, log: list,
                     guard: float) -> dict:
    # 1. waypoints on the axis, squaring up at each
    for back in DOCK_WAYPOINTS_MM:
        if back <= DOCK_GUARD_OFF_MM and guard > 0:
            # the dock's own tower is inside the TFMini's stop range from here in
            # (2026-10-26: 14 forward pulses refused 154 mm short of the 200 mm waypoint)
            await client.set_number("obstacle_stop", 0)
        wx, wy = _axis_point(pose, back)
        r = await go_to(x_px=wx, y_px=wy, stop_mm=80.0, camera=camera, max_steps=max_steps)
        log.append({"leg": f"waypoint {back:.0f} mm", **r.as_dict()})
        if not r.ok:
            return {"ok": False, "reason": f"waypoint {back:.0f}: {r.reason}", "log": log}
        f = await face(pose["heading_deg"], camera, 2.0)
        log.append({"leg": f"face at {back:.0f} mm", **f.as_dict()})
        if not f.ok:
            return {"ok": False, "reason": f"face at {back:.0f}: {f.reason}", "log": log}
    # 2. creep in, guard relaxed, overhead watching
    if guard > 0:
        await client.set_number("obstacle_stop", 0)
    prev = None
    stalls = 0
    steer_fails = 0
    for i in range(DOCK_MAX_CREEPS):
        rover, _ = _rover(camera)
        if rover is None:
            return {"ok": False, "reason": "rover marker lost while creeping", "log": log}
        dist_mm = math.hypot(rover.x_px - pose["x_px"], rover.y_px - pose["y_px"]) * pose["mm_per_px"]
        # signed progress along the axis: + = still short of the docked pose
        h = math.radians(pose["heading_deg"])
        along = ((rover.x_px - pose["x_px"]) * (-math.cos(h)) + (rover.y_px - pose["y_px"]) * math.sin(h)) * pose["mm_per_px"]
        entry = {"creep": i, "x": round(rover.x_px), "y": round(rover.y_px), "heading": rover.heading_deg,
                 "dist_mm": round(dist_mm), "short_mm": round(along)}
        if along <= DOCK_ARRIVE_MM:
            log.append({**entry, "action": "docked"})
            return {"ok": True, "reason": f"docked: {dist_mm:.0f} mm from the taught pose", "log": log,
                    "pose": _pose_dict(rover)}
        # signed sideways offset from the axis (+ = to Grover's left in the image frame);
        # the waypoints only arrive within 80 mm and `face` squares heading, not offset,
        # so steer back onto the axis while creeping (2026-10-26: 35 mm off tripped a cliff sensor)
        lateral = ((rover.x_px - pose["x_px"]) * (-math.sin(h)) + (rover.y_px - pose["y_px"]) * (-math.cos(h))) * pose["mm_per_px"]
        entry["lateral_mm"] = round(lateral)
        if abs(lateral) > DOCK_LATERAL_MM and along > 15.0:
            ax, ay = _axis_point(pose, max(along - DOCK_LOOKAHEAD_MM, 0.0))
            aim = math.degrees(math.atan2(-(ay - rover.y_px), ax - rover.x_px)) % 360
        else:
            # back on the axis (or too close to steer): square up again, or the
            # correction angle carries Grover across the axis (10-26: 12 mm one
            # way became 21 mm the other)
            aim = pose["heading_deg"]
        if along > 15.0 and abs(heading_change(rover.heading_deg, aim)) > 3.0 and steer_fails < 2:
            f = await face(aim, camera, 2.0)
            log.append({**entry, "action": f"steer to {aim:.1f}", "ok": f.ok})
            # a pivot this small often doesn't move the tracks at all (10-26: six
            # failed steers in a row); after two, creep on and let the offset grow
            steer_fails = 0 if f.ok else steer_fails + 1
            continue
        steer_fails = 0
        st = await client.state(timeout=3.0)
        if st.front_left_cliff or st.front_right_cliff:
            # The base is black plastic: the cliff sensors read it as no
            # floor and the firmware refuses forward (run 1, 2026-10-24).
            # White tape on the base under the sensor paths is the fix;
            # report rather than grind.
            log.append({**entry, "action": "cliff guard active on the dock"})
            return {"ok": along <= 60.0, "reason": f"cliff sensor active {along:.0f} mm short of the taught pose "
                    "(black base under the sensors? tape it white)", "log": log, "pose": _pose_dict(rover)}
        if prev is not None and math.hypot(rover.x_px - prev[0], rover.y_px - prev[1]) < DOCK_STALL_PX:
            stalls += 1
            if stalls >= 3:
                log.append({**entry, "action": "stalled"})
                # with the bumper bar (10-26) the wall is the stop: a stall within
                # DOCK_BUMP_MM of the pose is a dock, not a failure
                return {"ok": along <= DOCK_BUMP_MM, "reason": f"stalled {along:.0f} mm short of the taught pose",
                        "log": log, "pose": _pose_dict(rover)}
        else:
            stalls = 0
        prev = (rover.x_px, rover.y_px)
        creep = DOCK_CREEP_S * (1 + stalls)      # a stalled creep gets longer: the ramp lip needs more than a nudge
        log.append({**entry, "action": f"creep {creep:.2f}s"})
        await client.drive("forward", creep)
        await asyncio.sleep(POST_MOVE_S)
    return {"ok": False, "reason": "creep cap reached", "log": log}
