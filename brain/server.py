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
    """Current rover state: motion, battery voltage, cliff sensors, uptime, WiFi."""
    st = await RoverClient().state()
    return {
        "motion": st.motion,
        "battery_voltage": st.battery_voltage,
        "front_left_cliff": st.front_left_cliff,
        "front_right_cliff": st.front_right_cliff,
        "uptime_s": st.uptime_s,
        "wifi_dbm": st.wifi_dbm,
    }


@mcp.tool()
def snapshot(camera: str = "bench") -> Image:
    """Grab a still JPEG. camera = 'bench' (fixed workbench camera) or 'rover' (onboard T-Camera)."""
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
async def stop() -> dict:
    """Stop the motors now."""
    await RoverClient().stop()
    return {"ok": True}


if __name__ == "__main__":
    mcp.run()
