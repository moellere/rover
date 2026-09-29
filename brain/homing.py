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
import time
from dataclasses import dataclass, field

from brain.cameras import snapshot
from brain.markers import find_markers, Marker
from brain.rover_client import RoverClient

# Tunables - conservative on purpose.
CENTER_DEG = 6.0        # "centred" if |bearing| <= this (pivot granularity is ~5-7 deg)
PIVOT_S = 0.2           # initial pivot pulse length
PIVOT_MAX_S = 0.6       # adaptive cap: a pulse that doesn't turn the rover grows by 1.5x
PIVOT_MIN_EFFECT = 1.5  # deg of bearing change that counts as "it turned"
FORWARD_S = 0.3         # forward pulse length
FORWARD_NEAR_S = 0.15   # shorter step inside NEAR_MM so the stop isn't overshot
NEAR_MM = 350.0
STOP_MM = 200.0         # stop when the marker is this close
SETTLE_S = 2.5          # wait after a pulse before trusting a frame (motion blur)
MAX_PULSES = 20         # hard cap on drive pulses per run
MAX_LOST = 3            # consecutive frames without the marker -> give up


@dataclass
class HomingResult:
    ok: bool
    reason: str
    pulses: int
    final_bearing_deg: float | None
    final_distance_mm: float | None
    log: list = field(default_factory=list)


def _look(camera: str, marker_id: int) -> Marker | None:
    ms = find_markers(snapshot(camera), camera)
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
    pivot_s = PIVOT_S
    prev_bearing: float | None = None
    t0 = time.monotonic()
    try:
        while pulses < max_pulses:
            m = _look(camera, marker_id)
            if m is None:
                lost += 1
                log.append({"t": round(time.monotonic() - t0, 1), "seen": False})
                if lost >= MAX_LOST:
                    await client.stop()
                    return HomingResult(False, f"marker lost for {MAX_LOST} frames", pulses,
                                        last.bearing_deg if last else None, last.distance_mm if last else None, log)
                await asyncio.sleep(1.0)
                continue
            lost = 0
            last = m
            log.append({"t": round(time.monotonic() - t0, 1), "seen": True,
                        "bearing": round(m.bearing_deg, 1), "distance": round(m.distance_mm or -1)})
            if m.distance_mm is not None and m.distance_mm <= stop_mm and abs(m.bearing_deg) <= CENTER_DEG:
                await client.stop()
                return HomingResult(True, "arrived", pulses, m.bearing_deg, m.distance_mm, log)

            # Guards read from the rover before every pulse.
            st = await client.state(timeout=3.0)
            if st.battery_voltage is not None and st.battery_voltage < 9.6:
                await client.stop()
                return HomingResult(False, f"battery {st.battery_voltage:.2f} V", pulses, m.bearing_deg, m.distance_mm, log)
            if st.front_left_cliff or st.front_right_cliff:
                await client.stop()
                return HomingResult(False, "cliff sensor active", pulses, m.bearing_deg, m.distance_mm, log)

            if abs(m.bearing_deg) > CENTER_DEG:
                # Adapt the pulse: stiction means short pulses often do nothing.
                if prev_bearing is not None:
                    if abs(m.bearing_deg - prev_bearing) < PIVOT_MIN_EFFECT:
                        pivot_s = min(PIVOT_MAX_S, round(pivot_s * 1.5, 2))
                    else:
                        pivot_s = max(PIVOT_S, round(pivot_s / 1.5, 2))
                prev_bearing = m.bearing_deg
                # + bearing = marker is right of centre -> pivot right
                direction = "right" if m.bearing_deg > 0 else "left"
                await client.drive(direction, pivot_s)
                log[-1]["pulse"] = f"{direction} {pivot_s}s"
            elif m.distance_mm is None or m.distance_mm > stop_mm:
                prev_bearing = None
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
