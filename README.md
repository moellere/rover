# Grover

A small rover built from Makeblock parts, living on a garage workbench and
learning to look after itself. Named Grover on 2026-09-29: blue rails, and it
spends its life demonstrating *near... far*.

This repo is the whole project: a dated [journal](JOURNAL.md) of what
happened and who decided it, the [bill of materials](BOM.md) against a $100
budget, the [roadmap](ROADMAP.md), the off-board brain, printable hardware,
scripts, and a reference copy of the firmware.

It is a collaborative build between Enoch and Claude (Anthropic). The
journal records which model did the work at each stage and which decisions
were Claude-driven versus Enoch-directed. [CLAUDE.md](CLAUDE.md) is the
standing rulebook (mission, hard constraints, budget policy, permissions,
safety rules learned the hard way) - auto-loaded by Claude Code as project
instructions, and readable as plain English by anyone.

## The mission

1. **Phase 1 (current):** drive around the workbench without falling off.
2. **Phase 2:** recharge itself.
3. **Phase 3:** roam the house.

## Where it stands (2026-10-05)

- **Visual homing works.** `home_to_marker` finds a printed ArUco marker
  with the onboard camera and parks in front of it, unattended.
- **It has been through the house.** On 2026-10-04 Grover drove from the
  dining room through the foyer and living room to the kitchen doorway
  (~12-14 m) in short, camera-checked legs, stopping itself for a dog,
  people and sun glare. Hardwood and rugs both fine.
- **Spinal cord is an ESP32** (`rover32`, since 2026-10-03) with no I/O
  expander; the TFMini LiDAR sits alone on its own I2C bus.
- **Sensors:** TFMini forward LiDAR (obstacle stop at 50 cm), two TCRT5000
  cliff sensors on mounts that put each one ahead of its wheel, the rover
  camera, and two bench cameras (one behind, one head-on PTZ).
- **Chassis is the trike build** (two driven wheels, trailing caster). The
  swivel caster twists the rear on stops; a fixed printed skid
  (`hardware/caster-skid.scad`) replaces it next.
- **The house chassis works too:** a Eufy RoboVac 12 driven over IR from
  `blackcam`, a T-Camera on its lid (camera + IR LED driver). It has backed
  off its dock and returned on command.
- Known hazard: no rear cliff sensors, and reversing a trike is
  unpredictable - see the reversing rule in `CLAUDE.md`.

## Architecture

Three layers, decided early and still standing:

| Layer | Hardware | Role |
|---|---|---|
| **Spinal cord** | ESP32 devkit (`rover32`, since 2026-10-03; was a Wemos D1 Mini), ESPHome | reflexes: watchdog, disconnect-stop, cliff, battery and TFMini obstacle guards, kick start, optional brake-on-stop. Authoritative - nothing off-board can override them. |
| **Eyes** | TTGO T-Camera (ESP32-WROVER, OV2640), ESPHome | snapshot and stream endpoints; no decisions |
| **Brain** | `brain/` - Python + OpenCV, off-board | everything with judgment: marker detection, the homing loop, bounded drive pulses. Exposed as an MCP server (`rover-brain`). |

Claude (the model) is *not* in the control loop: it starts a run and reads
the log. A homing run is a plain Python loop - look, decide one pulse,
settle, look again - talking to the rover over ESPHome's native API.

## Hardware

- Chassis: Makeblock Starter Robot Kit, **trike** configuration; two DC gear
  motors, trailing swivel caster (to be replaced by a printed fixed skid)
- Controller: ESP32 devkit (`rover32`) - motor enables on GPIO16/17,
  direction on GPIO18/19/22/23, cliff inputs GPIO35/32, TFMini I2C on
  GPIO25/26, battery sense on GPIO34. (Was a Wemos D1 Mini + MCP23008.)
- Motor driver: L298N dual H-bridge
- Power: 3x 18650 Li-ion in 3S (12.6 V full); LM2596 buck at 5.2 V for the
  ESP32, the camera and the TFMini; battery voltage through a 100k/27k
  divider (calibrated to the meter). A 3S BMS board is in hand, not fitted.
- Sensing: Benewake TFMini LiDAR on a printed bracket (direct GH1.25 lead,
  5 V); two TCRT5000 cliff modules at 3.3 V on printed v4 mounts
- Vision: TTGO T-Camera on the rover (fisheye, ~111 deg); two Thingino
  cameras on the bench (`camv3` behind the rover, `fishcam` PTZ head-on)
- Homing targets: ArUco 4x4_50 markers, ids 0 (80 mm) and 1 (160 mm),
  printable from `hardware/markers/`

## Software

- **Firmware:** ESPHome (`firmware/rover32.yaml` for Grover,
  `firmware/blackcam.yaml` for the Eufy's lid board; `rover.yaml` and
  `eufy-ir.yaml` are retired - all reference copies; the live configs with
  secrets are in a private repo).
  Custom services `forward`/`backward`/`left`/`right`/`stop`; `Drive duty`
  `Pivot duty` and `Left trim` (+6 %, calibrated) sliders; a `Brake on stop` switch (boots off); `Obstacle stop` distance (50 cm).
- **Brain:** `brain/` - MCP tools `status`, `snapshot(bench|front|rover)`, `set_brake`, `set_obstacle_stop`,
  `drive` (capped at 1 s, refused on low battery or cliff), `find_marker`,
  `home_to_marker`, `stop`. Install with `scripts/install-brain.sh`; details
  in `brain/README.md`.
- **Printing:** parametric OpenSCAD in `hardware/` (camera cradle, adapter
  strip, TFMini bracket, cliff-sensor mounts, caster skid, marker pages, a
  shelved Roomba plug), sliced with the house rules
  (PETG, no brim, tree supports on auto) and printed through the
  print-warden service; toolchain via `scripts/install-tools.sh`.
- **Scripts:** `rover_ctl.py` (drive over the native API),
  `test_disconnect_safety.py` (proves the disconnect-stop),
  `camera_snapshot.py`, `warden_call.py` (talk to the print-warden from a
  shell). All read hosts and credentials from environment variables.

### Safety design

A device that can drive off a table needs more than "send stop when you
mean it." In the firmware, always on:

- **Command watchdog** - no drive command for 1.5 s -> motors stop.
- **Disconnect-stop** - the API client goes away for any reason -> motors
  stop. Verified by `scripts/test_disconnect_safety.py`.
- **Cliff guard** - a front IR sensor stops seeing the bench -> forward and
  pivots refused (backward stays allowed).
- **Battery guard** - below 9.3 V the rover refuses to drive; resumes above
  9.6 V. Rolling 25 s average, ignored for 20 s after boot (a latched-low
  bug from a bad first sample was fixed 2026-10-05).
- **Obstacle guard** - the TFMini (polled every 50 ms) refuses and cuts
  forward motion inside 50 cm; "was under 60 cm, now too close to measure"
  counts as an obstacle (a wall met at an angle slipped through before).
- **Kick start** - 100 ms at full power from rest so both wheels break
  stiction together, then the set duty and trim.
- **Brake-on-stop** (switch, boots off) - shorts the windings for 150 ms on
  every stop. Measured: no change in distance and it didn't stop the
  end-of-pulse yaw (the swivel caster did that).

The brain adds courtesy limits on top (pulse cap, gap between pulses,
lost-marker and stuck detection) but never replaces the firmware's.

## The house chassis: a Eufy RoboVac 12

Phases 2 and 3 ride on a **Eufy RoboVac 12**, keeping its own docking,
charging, cliff and bumper behaviour, driven over infrared. Its remote
sends a 6-byte frame `68 CMD HH MM 5C SUM` - **the current time is stamped
into every command**, and stale frames are ignored. `blackcam`, a T-Camera
on the lid (`firmware/blackcam.yaml`), stamps each frame from SNTP and
drives a 940 nm LED through an NPN transistor (~105 mA, 2 m range). It has
backed the Eufy off its dock and sent it home. See Tier 2E in the roadmap.

## First drive

![First look at the workbench, lights on](images/01-first-look.jpg)
![Mid-drive, having moved a full bench-length](images/02-first-drive.jpg)
![Parked safely after the session](images/03-parked-safe.jpg)

## Budget

Parts already in Enoch's inventory are supplied by him. Anything else comes
out of a standing **$100 budget** tracked in [BOM.md](BOM.md). Spent so far:
$0.00.

---

Built and driven in collaboration with Claude (Anthropic).
