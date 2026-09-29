"""
Rover brain - an MCP server that is the high-level front door to the rover.

Tools:
    status              motion, battery, cliff sensors, link quality
    snapshot(camera)    a JPEG from the bench camera or the rover's own camera
    drive(direction, s) a bounded pulse: forward/backward/left/right for at
                        most MAX_PULSE_S, always followed by stop
    stop                immediate stop

Safety here is a courtesy layer: the firmware's watchdog, disconnect-stop,
cliff and battery guards remain authoritative and cannot be bypassed from
this side. This server just refuses obviously bad requests early.

Run (stdio, for Claude Code):  brain/.venv/bin/python -m brain.server
All hosts and credentials come from environment variables - see
rover_client.py and cameras.py.
"""
import time

from mcp.server.fastmcp import FastMCP, Image

from brain.cameras import CAMERAS, snapshot as _snapshot
from brain.rover_client import DRIVE_SERVICES, RoverClient

MAX_PULSE_S = 1.0          # longest single drive pulse this server will issue
MIN_GAP_S = 0.3            # breathing room between pulses
LOW_BATTERY_V = 9.6        # refuse to drive below this (firmware cuts at 9.3)

mcp = FastMCP("rover-brain")
_last_drive_end = 0.0


@mcp.tool()
async def status() -> dict:
    """Current rover state: motion, battery voltage, cliff sensors, uptime, WiFi,
    and whether stops brake."""
    st = await RoverClient().state()
    return {
        "motion": st.motion,
        "battery_voltage": st.battery_voltage,
        "front_left_cliff": st.front_left_cliff,
        "front_right_cliff": st.front_right_cliff,
        "uptime_s": st.uptime_s,
        "wifi_dbm": st.wifi_dbm,
        "brake_on_stop": st.brake_on_stop,
    }


@mcp.tool()
def snapshot(camera: str = "bench") -> Image:
    """Grab a still JPEG. camera = 'bench' (fixed, behind the rover's start end,
    sees its rear), 'front' (across the bench, sees the rover head-on and the
    long left edge) or 'rover' (onboard T-Camera)."""
    if camera not in CAMERAS:
        raise ValueError(f"camera must be one of {CAMERAS}")
    return Image(data=_snapshot(camera), format="jpeg")


@mcp.tool()
async def drive(direction: str, seconds: float = 0.5) -> dict:
    """Pulse the rover: direction in forward/backward/left/right, for `seconds`
    (capped at 1.0). Left/right are in-place pivots. Always ends with stop."""
    global _last_drive_end
    if direction not in DRIVE_SERVICES:
        raise ValueError(f"direction must be one of {DRIVE_SERVICES}")
    seconds = max(0.05, min(float(seconds), MAX_PULSE_S))
    gap = time.monotonic() - _last_drive_end
    if gap < MIN_GAP_S:
        time.sleep(MIN_GAP_S - gap)
    client = RoverClient()
    st = await client.state(timeout=3.0)
    if st.battery_voltage is not None and st.battery_voltage < LOW_BATTERY_V:
        return {"ok": False, "reason": f"battery {st.battery_voltage:.2f}V below {LOW_BATTERY_V}V"}
    if direction != "backward" and (st.front_left_cliff or st.front_right_cliff):
        return {"ok": False, "reason": "cliff sensor active; only backward allowed"}
    await client.drive(direction, seconds)
    _last_drive_end = time.monotonic()
    return {"ok": True, "direction": direction, "seconds": seconds}


@mcp.tool()
def find_marker(camera: str = "rover") -> dict:
    """Look for ArUco homing markers in a fresh frame from `camera` ('rover',
    'bench' or 'front'). Returns each marker's id, pixel centre, apparent size, bearing in
    degrees (+ = right of centre) and distance in mm (None until the camera is
    calibrated - see brain/markers.py)."""
    from brain.markers import markers_as_dicts
    if camera not in CAMERAS:
        raise ValueError(f"camera must be one of {CAMERAS}")
    found = markers_as_dicts(_snapshot(camera), camera)
    return {"camera": camera, "count": len(found), "markers": found}


@mcp.tool()
async def home_to_marker(marker_id: int = 0, stop_mm: float = 200.0, max_pulses: int = 20) -> dict:
    """Autonomously drive to an ArUco marker seen by the rover's camera: pivot
    until centred, step forward until `stop_mm` away, re-measuring after every
    pulse. Stops on a lost marker, a cliff, low battery, or the pulse cap."""
    from brain.homing import home_to_marker as _home
    r = await _home(marker_id, "rover", stop_mm, max_pulses)
    return {"ok": r.ok, "reason": r.reason, "pulses": r.pulses,
            "final_bearing_deg": r.final_bearing_deg, "final_distance_mm": r.final_distance_mm, "log": r.log}


@mcp.tool()
async def set_brake(on: bool) -> dict:
    """Turn the firmware's brake-on-stop on (default) or off. Off only for A/B
    tests - every stop path still stops, it just coasts."""
    await RoverClient().set_switch("brake_on_stop", on)
    st = await RoverClient().state(timeout=3.0)
    return {"ok": st.brake_on_stop == on, "brake_on_stop": st.brake_on_stop}


@mcp.tool()
async def stop() -> dict:
    """Stop the motors now."""
    await RoverClient().stop()
    return {"ok": True}


if __name__ == "__main__":
    mcp.run()
