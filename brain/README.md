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
| `find_marker(camera)` | ArUco 4x4_50 markers in a fresh frame: id, pixel centre, apparent size, bearing (+ = right), distance in mm (per-camera calibration via `BENCH_CAM_FOCAL_PX` / `ROVER_CAM_FOCAL_PX`; bench cam calibrated 2026-09-29 at 1062 px, rover cam at 437 px - a ~111 deg fisheye, so the 80 mm marker decodes only within ~1 m; use the 160 mm id-1 marker beyond that) | - |
| `stop` | stop now | - |

Orientation note: on the bench, `forward` moves the rover away from the fixed
bench camera (the camera sees its rear); `backward` moves it toward the
camera and the near edge.

Planned: `home_to_marker` - closed-loop approach to the marker - once the camera
is mounted and calibrated (`ROVER_CAM_FOCAL_PX`, see `markers.py`). The
printable marker is `hardware/markers/aruco_4x4_50_id0_80mm.png`.

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

## Bench camera day/night

The Thingino bench camera can be forced between modes for night-time marker
work: `GET /x/json-imp.cgi?cmd=daynight&val=night` (or `day`, `read`);
its IR floodlights toggle with `cmd=ir850|ir940&val=0|1`. Restore `day`
afterwards.
