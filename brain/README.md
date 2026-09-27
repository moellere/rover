# Rover brain (MCP server)

The high-level front door to the rover: an MCP server that Claude (or any
MCP client) talks to instead of poking ESPHome services and camera URLs by
hand. It runs off-board - on the dev VM today, on the cluster later - and
is where autonomy (visual homing, docking) will be written.

Architecture, for the record: the D1 Mini stays the *spinal cord* (ESPHome;
watchdog, disconnect-stop, cliff and battery guards in firmware), the
T-Camera stays the *eyes* (ESPHome; snapshot/stream), and this service is
the *brain*. The firmware guards are authoritative; this server only adds a
courtesy layer that refuses obviously bad requests early.

## Tools

| Tool | What it does | Limits |
|---|---|---|
| `status` | motion, battery voltage, both cliff sensors, uptime, WiFi dBm | - |
| `snapshot(camera)` | JPEG from `bench` (fixed workbench cam) or `rover` (onboard T-Camera) | - |
| `drive(direction, seconds)` | pulse `forward`/`backward`/`left`/`right`, then stop | capped at 1.0 s per call, 0.3 s gap between pulses, refused below 9.6 V or when a cliff sensor is active (backward still allowed) |
| `stop` | stop now | - |

Planned: `home_to_marker` (find a printed marker with the onboard camera,
park nose-on) once the camera is mounted.

## Install and run

```
scripts/install-brain.sh            # venv at brain/.venv with the MCP SDK, aioesphomeapi, OpenCV
cp brain/env.example ~/.rover-brain.env && $EDITOR ~/.rover-brain.env
brain/run.sh                        # stdio server (what an MCP client launches)
```

Register with Claude Code so it appears as a tool set in every session:

```
claude mcp add rover-brain --scope user -- /path/to/rover/brain/run.sh
```

No host, key, or password is stored in this repo or in the MCP registration
- `run.sh` reads them from `~/.rover-brain.env` at launch.

## Files

- `server.py` - the MCP server (FastMCP) and its safety limits
- `rover_client.py` - ESPHome native-API wrapper (state, drive, stop)
- `cameras.py` - still-frame capture from both cameras
- `run.sh` - launcher; `env.example` - the variables it expects
