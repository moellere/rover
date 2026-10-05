"""
Rover brain - an MCP server that is the high-level front door to the rover.

Tools:
    status              motion, battery, cliff sensors, link quality
    snapshot(camera)    a JPEG from bench (overhead), front, rover or eufy
    locate(camera)      overhead marker poses - Grover's position and heading
    eufy(command)       drive the Eufy RoboVac over IR via its lid board
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
import os
import time

from mcp.server.fastmcp import FastMCP, Image

from brain.cameras import CAMERAS, snapshot as _snapshot
from brain.rover_client import DRIVE_SERVICES, RoverClient

MAX_PULSE_S = 1.0          # longest single drive pulse this server will issue
MIN_GAP_S = 0.3            # breathing room between pulses
LOW_BATTERY_V = 9.6        # refuse to drive below this (firmware cuts at 9.3)

# Transport: stdio by default (Claude Code launches brain/run.sh); set
# BRAIN_TRANSPORT=http to serve Streamable HTTP at /mcp (the container).
# Behind a reverse proxy FastMCP's DNS-rebinding check 421s the public Host
# header; BRAIN_ALLOWED_HOSTS lists the names to accept (host and host:*),
# BRAIN_DNS_REBINDING_PROTECTION=false disables the check (the cluster
# ingress only routes the exact hostname, behind basic auth).
from mcp.server.transport_security import TransportSecuritySettings
_hosts = [h for h in os.environ.get("BRAIN_ALLOWED_HOSTS", "").split(",") if h]
_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=os.environ.get("BRAIN_DNS_REBINDING_PROTECTION", "true") != "false",
    allowed_hosts=_hosts or ["localhost", "localhost:*", "127.0.0.1", "127.0.0.1:*"])
mcp = FastMCP("rover-brain", host=os.environ.get("BRAIN_HOST", "0.0.0.0"),
              port=int(os.environ.get("BRAIN_PORT", "8000")), transport_security=_security)
_last_drive_end = 0.0


@mcp.tool()
async def status() -> dict:
    """Current rover state: motion, battery voltage, cliff sensors, uptime, WiFi,
    whether stops brake, and the TFMini forward range (cm; valid=False under
    30 cm or with no return) plus the firmware obstacle-stop threshold."""
    st = await RoverClient().state()
    return {
        "motion": st.motion,
        "battery_voltage": st.battery_voltage,
        "front_left_cliff": st.front_left_cliff,
        "front_right_cliff": st.front_right_cliff,
        "uptime_s": st.uptime_s,
        "wifi_dbm": st.wifi_dbm,
        "brake_on_stop": st.brake_on_stop,
        "front_range_cm": st.front_range_cm,
        "front_range_valid": st.front_range_valid,
        "obstacle_stop_cm": st.obstacle_stop_cm,
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
    """Turn the firmware's brake-on-stop on or off (it boots off). Every stop
    path still stops either way; off just coasts."""
    await RoverClient().set_switch("brake_on_stop", on)
    st = await RoverClient().state(timeout=3.0)
    return {"ok": st.brake_on_stop == on, "brake_on_stop": st.brake_on_stop}


@mcp.tool()
async def set_obstacle_stop(cm: float) -> dict:
    """Set the firmware's forward obstacle guard (TFMini): forward is refused,
    and a forward move stopped, while something is closer than `cm`. 0 turns
    it off. The TFMini can't see under 30 cm, so a docking approach lowers or
    clears this for its last stretch and relies on the camera there."""
    await RoverClient().set_number("obstacle_stop", float(cm))
    st = await RoverClient().state(timeout=3.0)
    return {"ok": st.obstacle_stop_cm == float(cm), "obstacle_stop_cm": st.obstacle_stop_cm}


@mcp.tool()
def locate(camera: str = "bench") -> dict:
    """Where are the markers on the bench, seen from the overhead camera?
    Grover carries ArUco id 2 (60 mm) on its top, FRONT edge toward its nose,
    so id 2's heading is Grover's heading. Angles are in the image frame:
    0 = image right, 90 = image up (CCW +); with fishcam's mount the homing
    marker end is 180 and the open garage-side edge is 90. mm_per_px is the
    local scale from the marker's printed size (approximate away from the
    image centre - wide lens)."""
    from brain.overhead import poses_as_dicts, ROVER_TOP_ID
    if camera not in CAMERAS:
        raise ValueError(f"camera must be one of {CAMERAS}")
    found = poses_as_dicts(_snapshot(camera))
    rover = next((p for p in found if p["id"] == ROVER_TOP_ID), None)
    return {"camera": camera, "rover": rover, "markers": found}


@mcp.tool()
async def eufy(command: str) -> dict:
    """Drive the Eufy RoboVac 12 over IR via its lid board: forward, backward,
    left, right, home (return to dock) or start_stop (start/stop cleaning).
    Each command is one remote button press. The Eufy works on the FLOOR only
    - it has no bench guards (CLAUDE.md). Watch it with snapshot('eufy')."""
    from brain.eufy_client import COMMANDS, EufyClient
    if command not in COMMANDS:
        raise ValueError(f"command must be one of {sorted(COMMANDS)}")
    code = await EufyClient().send(command)
    return {"ok": True, "command": command, "code": f"0x{code:02X}"}


@mcp.tool()
async def stop() -> dict:
    """Stop the motors now."""
    await RoverClient().stop()
    return {"ok": True}


if __name__ == "__main__":
    if os.environ.get("BRAIN_TRANSPORT", "stdio") == "http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run()
