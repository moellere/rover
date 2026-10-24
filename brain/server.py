"""
Rover brain - an MCP server that is the high-level front door to the rover.

Tools:
    status              motion, battery, cliff sensors, link quality
    snapshot(camera)    a JPEG from bench (overhead), front, rover or eufy
    locate(camera)      overhead marker poses - Grover's position and heading
    eufy(command)       drive the Eufy RoboVac over IR via its lid board
    drive(direction, s) a bounded pulse: forward/backward/left/right for at
                        most MAX_PULSE_S of cruise, ramped up and down by the
                        firmware (2026-10-18), always ending stopped
    set_ramp(...)       the firmware's min duty / accel / decel sliders
    turn(degrees)       gyro-closed pivot on the ESP32 (2026-10-19 firmware)
    face(heading)       turn until the overhead camera sees that heading
    go_to(...)          drive to a marker or pixel target, closed on the overhead
    stop                immediate stop (no decel ramp)

Safety here is a courtesy layer: the firmware's watchdog, disconnect-stop,
cliff and battery guards remain authoritative and cannot be bypassed from
this side. This server just refuses obviously bad requests early.

Run (stdio, for Claude Code):  brain/.venv/bin/python -m brain.server
All hosts and credentials come from environment variables - see
rover_client.py and cameras.py.
"""
import os
import time
from typing import Optional

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
        "ramp": {"min_duty_pct": st.min_duty, "accel_ms": st.accel_ms, "decel_ms": st.decel_ms},
        "yaw_deg": st.yaw_deg,
        "yaw_rate_dps": st.yaw_rate_dps,
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
    of cruise (capped at 1.0), timed on the ESP32. The firmware jumps to its
    min duty, ramps up to the drive/pivot duty, cruises, then ramps down over
    its decel time (see set_ramp) - so a 0.3 s pulse moves for ~0.6 s. Left/
    right are in-place pivots. Always ends stopped."""
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
    0 = image right, 90 = image up (CCW +); with benchcam's mount the homing
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
async def turn(degrees: float, duty: int = 0) -> dict:
    """Pivot in place by `degrees` (+ = left/CCW, - = right), closed on the
    rover's gyro: the firmware ramps up, watches its yaw, and eases out
    `turn_lead` degrees before the goal (3 s hard cap). Returns the yaw
    before and after. Needs the gyro wired and calibrated (status.yaw_deg
    not None); on the tank, pivots scrub, so this is the only repeatable
    way to turn."""
    global _last_drive_end
    c = RoverClient()
    before = (await c.state(timeout=3.0)).yaw_deg
    if before is None:
        raise RuntimeError("gyro not reporting - wired and calibrated?")
    await c.turn(degrees, duty)
    _last_drive_end = time.monotonic()
    after = (await c.state(timeout=3.0)).yaw_deg
    return {"ok": True, "requested_deg": degrees, "yaw_before": before, "yaw_after": after,
            "turned_deg": None if after is None else round(after - before, 1)}


@mcp.tool()
async def face(heading_deg: float, tol_deg: float = 3.0, camera: str = "bench") -> dict:
    """Turn Grover until the overhead camera reads its heading within `tol_deg`
    of `heading_deg` (image frame: 0 = right, 90 = up, 180 = toward the homing
    marker end, 270 = toward the pegboard). Each correction is a gyro-closed
    turn; the overhead is re-read after every one. Needs the id 2 marker on
    Grover's top in view."""
    global _last_drive_end
    from brain.steer import face as _face
    r = await _face(heading_deg, camera, tol_deg)
    _last_drive_end = time.monotonic()
    return r.as_dict()


@mcp.tool()
async def go_to(marker_id: Optional[int] = None, x_px: Optional[float] = None, y_px: Optional[float] = None,
                stop_mm: float = 150.0, max_steps: int = 10, camera: str = "bench") -> dict:
    """Drive Grover to a target seen by the overhead camera - another marker's
    position (`marker_id`, e.g. 0 lying flat as the goal spot) or a pixel
    (`x_px`, `y_px`) - and stop within `stop_mm` of it. Loop: locate, turn
    toward the target if more than 10 deg off, else one forward pulse sized
    from the distance (never longer than 1 s), re-locate. Check the lane on
    the overhead first: the firmware's TFMini guard only covers straight
    ahead. Returns the step log."""
    global _last_drive_end
    from brain.steer import go_to as _go_to
    r = await _go_to(x_px, y_px, marker_id, stop_mm, camera, max_steps)
    _last_drive_end = time.monotonic()
    return r.as_dict()


@mcp.tool()
async def dock_approach(goal_marker: int = 0, final_marker: int = 1, final_stop_mm: float = 120.0) -> dict:
    """Overhead `go_to` the goal-spot marker (stops 45 cm out, nose on it), then
    the onboard camera's `home_to_marker` on the upright marker behind it.
    The front half of docking. Check the lane on the overhead first."""
    global _last_drive_end
    from brain.steer import dock_approach as _dock
    r = await _dock(goal_marker, final_marker, final_stop_mm)
    _last_drive_end = time.monotonic()
    return r


@mcp.tool()
async def set_ramp(min_duty_pct: Optional[float] = None, accel_ms: Optional[float] = None,
                   decel_ms: Optional[float] = None) -> dict:
    """Tune the firmware's speed profile (persisted on the rover). min_duty_pct
    is applied at once from rest so both wheels break stiction together
    (default 40); accel_ms / decel_ms are the time to sweep the full 0..100%
    range (default 300 each). 0 ms = step. Guards never ramp. Pass only the
    values to change."""
    c = RoverClient()
    if min_duty_pct is not None:
        await c.set_number("min_duty", float(min_duty_pct))
    if accel_ms is not None:
        await c.set_number("accel_time", float(accel_ms))
    if decel_ms is not None:
        await c.set_number("decel_time", float(decel_ms))
    st = await c.state(timeout=3.0)
    return {"min_duty_pct": st.min_duty, "accel_ms": st.accel_ms, "decel_ms": st.decel_ms}


@mcp.tool()
async def stop() -> dict:
    """Stop the motors now - immediate, no decel ramp."""
    await RoverClient().halt()
    return {"ok": True}


if __name__ == "__main__":
    if os.environ.get("BRAIN_TRANSPORT", "stdio") == "http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run()
