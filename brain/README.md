# Rover brain (MCP server)

The high-level front door to the rover: an MCP server that Claude (or any
MCP client) talks to instead of poking ESPHome services and camera URLs by
hand. It runs off-board - on the dev VM today, on the cluster later - and
is where autonomy (visual homing, docking) will be written.

Architecture, for the record: an ESP32 (`rover32`) is the *spinal cord*
(ESPHome; watchdog, disconnect-stop, cliff, battery and obstacle guards in
firmware), the
T-Camera stays the *eyes* (ESPHome; snapshot/stream), and this service is
the *brain*. The firmware guards are authoritative; this server only adds a
courtesy layer that refuses obviously bad requests early.

## Tools

| Tool | What it does | Limits |
|---|---|---|
| `status` | motion, battery voltage, both cliff sensors, uptime, WiFi dBm, `brake_on_stop`, TFMini `front_range_cm`/`front_range_valid`, `obstacle_stop_cm` | - |
| `snapshot(camera)` | JPEG from `bench` (camv3, behind the rover), `front` (fishcam, across the bench, head-on) or `rover` (onboard T-Camera) | - |
| `drive(direction, seconds)` | pulse `forward`/`backward`/`left`/`right`, then stop | capped at 1.0 s per call, 0.3 s gap between pulses, refused below 9.6 V or when a cliff sensor is active (backward still allowed) |
| `find_marker(camera)` | ArUco 4x4_50 markers in a fresh frame: id, pixel centre, apparent size, bearing (+ = right), distance in mm (per-camera calibration via `BENCH_CAM_FOCAL_PX` / `ROVER_CAM_FOCAL_PX`; bench cam calibrated 2026-09-29 at 1062 px, rover cam at 437 px, front cam not yet (`FRONT_CAM_FOCAL_PX`). A CLAHE contrast pass retries frames where plain detection finds nothing (backlit marker) - a ~111 deg fisheye, so the 80 mm marker decodes only within ~1 m; use the 160 mm id-1 marker beyond that) | - |
| `set_obstacle_stop(cm)` | firmware TFMini guard distance; 0 = off. Boots at 50; `home_to_marker` relaxes it once the camera has the marker inside that distance, and restores it after | - |
| `set_brake(on)` | firmware `Brake on stop` switch (boots off) | - |
| `locate(camera)` | overhead marker poses: Grover's position and heading from ArUco id 2 (60 mm, taped on top, FRONT edge to the nose; page in `hardware/markers/`), plus any other markers; image-frame angles, local mm/px | - |
| `eufy(command)` | drive the Eufy RoboVac 12 over IR via its lid board: forward, backward, left, right, home, start_stop (one remote press each; floor only) | - |
| `stop` | stop now | - |

Orientation note: on the bench, `forward` moves the rover away from the fixed
bench camera (the camera sees its rear); `backward` moves it toward the
camera and the near edge.

`home_to_marker(marker_id, stop_mm, max_pulses)` - the closed loop in
`homing.py`: look with the rover camera, pivot toward the marker if it's off
centre, else step forward, settle, look again. Per-direction adaptive pivot
pulses, a stuck guard, retries on transient camera errors, and arrival by
lateral offset (the big marker overfills the frame inside ~200 mm, which
counts as arrived). Printable markers: `hardware/markers/` (id 0 = 80 mm,
id 1 = 160 mm; use id 1 beyond ~1 m). Reversing is deliberately not part of
the loop - see the reversing rule in the project `CLAUDE.md`.

## Hosting

**Hosted since 2026-10-05** on the home Kubernetes cluster: Argo CD app
`app-rover-brain` (moellere/argocd, `applications/rover-brain/`), namespace
`rover-brain`, image `ghcr.io/moellere/rover:X.Y.Z` (built by
`.github/workflows/brain-image.yml` on `v*` tags - bump the tag in the
argocd manifest to deploy), endpoint `https://rover-brain.dorktool.com/mcp`
behind Traefik basic auth; credentials as SealedSecrets. Placement chosen by
the homelab-helper session. The user-scope `claude mcp` entry `rover-brain`
points there; `rover-brain-local` is the stdio copy on the dev VM.

`brain/Dockerfile` builds a container that serves **Streamable HTTP on
:8000 at `/mcp`** (`BRAIN_TRANSPORT=http`). Locally it still runs over
stdio via `brain/run.sh`. Every host, key and password comes from the
environment (`brain/env.example` lists them) - in the cluster, a Secret.

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
