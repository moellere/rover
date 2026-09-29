"""
Visual homing: drive the rover to a marker using its own camera.

Closed loop, deliberately simple:
    look -> if the marker is off-centre, pivot a short pulse toward it
         -> else if it's still far, step forward a short pulse
         -> settle, look again
Every pulse is short and re-measured, so lumpy motor response (the first
pulse after idle often does nothing; right pivots bite harder than left)
is corrected on the next look instead of accumulating.

Safety: the firmware guards stay authoritative (watchdog, disconnect-stop,
cliff, battery). This loop adds: a hard cap on total pulses, a cap on
consecutive frames without the marker (then stop), refusal to step forward
unless the marker was seen in the frame just taken, and a stop distance
that keeps the rover short of the marker.

Environment (see brain/rover_client.py, brain/cameras.py, brain/markers.py):
ROVER_HOST / ROVER_API_KEY / ROVER_CAM_HOST / ROVER_CAM_FOCAL_PX.
"""
import asyncio
import math
import time
from dataclasses import dataclass, field

from brain.cameras import snapshot
from brain.markers import find_markers, Marker
from brain.rover_client import RoverClient

# Tunables - conservative on purpose.
CENTER_DEG = 6.0        # "centred" if |bearing| <= this (pivot granularity is ~5-7 deg)
PIVOT_S = 0.1           # initial pivot pulse length (0.15 s was ~14 deg at 100% duty and
                        # ping-ponged across the 6 deg tolerance)
PIVOT_MAX_S = 1.0       # adaptive cap: a pulse that doesn't turn the rover grows by 1.5x
                        # (the server's MAX_PULSE_S). Left/right are tracked separately:
                        # at 75% duty the left pivot needed ~4x the pulse of the right;
                        # firmware now pivots at 100% and the two are symmetric.
PIVOT_MIN_EFFECT = 1.5  # deg of bearing change that counts as "it turned"
FORWARD_S = 0.3         # forward pulse length
FORWARD_NEAR_S = 0.1    # shorter step inside NEAR_MM so the stop isn't overshot
                        # (trike: 0.15 s went 247 -> 168 mm, past the 200 mm stop)
NEAR_MM = 350.0
STOP_MM = 200.0         # stop when the marker is this close
ARRIVE_LATERAL_MM = 30.0  # ...or within this sideways offset (d*sin(bearing)) at the stop distance
CLOSE_LOST_FACTOR = 1.25  # marker lost inside stop_mm*this after a pulse = it overfilled the frame
SETTLE_S = 1.5          # wait after a pulse before looking (motion blur); _look adds its own second frame
MAX_PULSES = 20         # hard cap on drive pulses per run
MAX_LOST = 3            # consecutive frames without the marker -> give up
STUCK_PULSES = 3        # consecutive pulses with no measurable change -> stop (don't grind)
STUCK_DEG = 0.5
STUCK_MM = 15.0


@dataclass
class HomingResult:
    ok: bool
    reason: str
    pulses: int
    final_bearing_deg: float | None
    final_distance_mm: float | None
    log: list = field(default_factory=list)


LOOK_RETRIES = 3        # transient camera errors (reboot, busy HTTP server) before giving up


def _look(camera: str, marker_id: int) -> Marker | None:
    # The camera's snapshot endpoint returns its most recent captured frame,
    # which can predate the last pulse. Grab one, wait longer than the
    # camera's idle frame period (1 fps), and use a second.
    # A failed fetch is retried a few times: the rover is stopped between
    # pulses, so waiting out a camera hiccup is safe; aborting the run isn't
    # any safer and loses the approach.
    for attempt in range(LOOK_RETRIES):
        try:
            snapshot(camera)
            time.sleep(1.2)
            ms = find_markers(snapshot(camera), camera)
            break
        except OSError:
            if attempt == LOOK_RETRIES - 1:
                raise
            time.sleep(2.0)
    for m in ms:
        if m.id == marker_id:
            return m
    return None


async def home_to_marker(marker_id: int = 0, camera: str = "rover",
                         stop_mm: float = STOP_MM, max_pulses: int = MAX_PULSES) -> HomingResult:
    client = RoverClient()
    log: list = []
    pulses = 0
    lost = 0
    last: Marker | None = None
    pivot_s = {"left": PIVOT_S, "right": PIVOT_S}   # adaptive, per direction
    prev_bearing: float | None = None
    prev_dir: str | None = None
    stuck = 0
    prev_obs: tuple[float, float | None] | None = None
    t0 = time.monotonic()
    try:
        while pulses < max_pulses:
            m = _look(camera, marker_id)
            if m is None:
                lost += 1
                log.append({"t": round(time.monotonic() - t0, 1), "seen": False})
                if lost >= MAX_LOST:
                    await client.stop()
                    # Close in, the marker overfills the frame (its border gets
                    # cropped and detection fails) - that's arrival, not loss.
                    if last is not None and last.distance_mm is not None and pulses > 0 \
                       and last.distance_mm <= stop_mm * CLOSE_LOST_FACTOR \
                       and abs(last.distance_mm * math.sin(math.radians(last.bearing_deg))) <= 2 * ARRIVE_LATERAL_MM:
                        return HomingResult(True, "arrived (marker filled the frame)", pulses,
                                            last.bearing_deg, last.distance_mm, log)
                    return HomingResult(False, f"marker lost for {MAX_LOST} frames", pulses,
                                        last.bearing_deg if last else None, last.distance_mm if last else None, log)
                await asyncio.sleep(1.0)
                continue
            lost = 0
            last = m
            log.append({"t": round(time.monotonic() - t0, 1), "seen": True,
                        "bearing": round(m.bearing_deg, 1), "distance": round(m.distance_mm or -1)})
            if m.distance_mm is not None and m.distance_mm <= stop_mm:
                lateral = abs(m.distance_mm * math.sin(math.radians(m.bearing_deg)))
                if abs(m.bearing_deg) <= CENTER_DEG or lateral <= ARRIVE_LATERAL_MM:
                    await client.stop()
                    return HomingResult(True, "arrived", pulses, m.bearing_deg, m.distance_mm, log)

            # Stuck guard: pulses that change nothing mean the rover is held up
            # (cable, mat edge, obstacle). Stop instead of grinding the motors.
            # A pivot that hasn't yet grown to PIVOT_MAX_S doesn't count - short
            # pulses below stiction are expected to do nothing at first.
            obs = (m.bearing_deg, m.distance_mm)
            no_change = prev_obs is not None and pulses > 0 and abs(obs[0] - prev_obs[0]) < STUCK_DEG and \
                (obs[1] is None or prev_obs[1] is None or abs(obs[1] - prev_obs[1]) < STUCK_MM)
            pivot_maxed = prev_dir is None or pivot_s[prev_dir] >= PIVOT_MAX_S
            if no_change and pivot_maxed:
                stuck += 1
                if stuck >= STUCK_PULSES:
                    await client.stop()
                    return HomingResult(False, f"stuck: no movement over {STUCK_PULSES} pulses", pulses,
                                        m.bearing_deg, m.distance_mm, log)
            else:
                stuck = 0
            prev_obs = obs

            # Guards read from the rover before every pulse.
            st = await client.state(timeout=3.0)
            if st.battery_voltage is not None and st.battery_voltage < 9.6:
                await client.stop()
                return HomingResult(False, f"battery {st.battery_voltage:.2f} V", pulses, m.bearing_deg, m.distance_mm, log)
            if st.front_left_cliff or st.front_right_cliff:
                await client.stop()
                return HomingResult(False, "cliff sensor active", pulses, m.bearing_deg, m.distance_mm, log)

            if abs(m.bearing_deg) > CENTER_DEG:
                # + bearing = marker is right of centre -> pivot right
                direction = "right" if m.bearing_deg > 0 else "left"
                # Adapt the pulse per direction: stiction means short pulses
                # often do nothing, and the two directions differ a lot.
                if prev_bearing is not None and prev_dir == direction:
                    if abs(m.bearing_deg - prev_bearing) < PIVOT_MIN_EFFECT:
                        pivot_s[direction] = min(PIVOT_MAX_S, round(pivot_s[direction] * 1.5, 2))
                    else:
                        pivot_s[direction] = max(PIVOT_S, round(pivot_s[direction] / 1.5, 2))
                prev_bearing = m.bearing_deg
                prev_dir = direction
                await client.drive(direction, pivot_s[direction])
                log[-1]["pulse"] = f"{direction} {pivot_s[direction]}s"
            elif m.distance_mm is None or m.distance_mm > stop_mm:
                prev_bearing = None
                prev_dir = None
                step = FORWARD_NEAR_S if (m.distance_mm is not None and m.distance_mm < NEAR_MM) else FORWARD_S
                await client.drive("forward", step)
                log[-1]["pulse"] = f"forward {step}s"
            pulses += 1
            await asyncio.sleep(SETTLE_S)
        await client.stop()
        return HomingResult(False, f"pulse cap {max_pulses} reached", pulses,
                            last.bearing_deg if last else None, last.distance_mm if last else None, log)
    except Exception as e:  # never leave the motors ambiguous
        try:
            await client.stop()
        except Exception:
            pass
        return HomingResult(False, f"error: {e}", pulses,
                            last.bearing_deg if last else None, last.distance_mm if last else None, log)


if __name__ == "__main__":
    import json, sys
    mid = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    r = asyncio.run(home_to_marker(mid))
    print(json.dumps(r.__dict__, indent=1))
