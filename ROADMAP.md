# Roadmap

Claude's proposed sequence of capabilities, written 2026-09-28 (Fable 5.1)
at Enoch's request. Ordered by dependency, not by fun - though there's fun
in every tier. Budget notes assume the $100 pool in `BOM.md`; "inventory"
means Enoch already has it. Enoch reshapes this freely; it's a proposal.

## Tier 0 - finish the bench (Phase 1 close-out)

| # | Item | Needs | Why |
|---|---|---|---|
| 0.1 | ~~Print and fit the camera mount~~ **done** (v5) | - | everything visual depends on it |
| 0.1a | ~~Rebuild the chassis as the trike~~ **done 2026-09-29** (drive wheels front, caster rear) | - | the tank skidded its tracks to pivot - stiction, asymmetry, 100% duty bursts; wheels pivot cleanly at low duty. Decided 2026-09-29. Then re-tune `PIVOT_S`/`FORWARD_S` in `brain/homing.py` |
| 0.1b | ~~Camera adapter strip fitted~~ **done 2026-09-29** | - | bolts the cradle to the front standoffs so bearings stop drifting with every pulse |
| 0.2 | ~~Camera on rover power~~ **done** (buck -> spliced USB) | - | camera travels with the rover |
| 0.3 | ~~Camera firmware for the rover role~~ **done** (5 fps idle, PSRAM) | - | snapshots are fresh; stream still SXGA - drop to VGA if latency matters |
| 0.4 | Cliff sensors installed | sensors (ordered), polarity check | the firmware guards are already waiting for them |
| 0.5 | Brain driving verified | rover powered on | `status` + a short `drive` pulse through the MCP server; calibrate seconds-per-cm and seconds-per-degree for pivots |
| 0.6 | Home Assistant cleanup | - | re-add the rover so battery/motion/cliff show on the dashboard; add both camera feeds to the workbench section |

## Tier 1 - visual homing (the proposed next goal)

Success test: from anywhere on the bench, the rover finds the marker and
parks nose-on within ~2 cm, unattended.

| # | Item | Needs | Notes |
|---|---|---|---|
| 1.1 | Printed marker | paper, `hardware/markers/` (done) | ArUco 4x4, id 0, 80 mm - printable page committed |
| 1.2 | `find_marker` tool | camera mounted | detector already in `brain/markers.py`; returns id, pixel centre, apparent size, bearing |
| 1.3 | Camera calibration | a ruler and the marker | focal length from marker size at known distances -> distance estimate |
| 1.4 | `home_to_marker` | 1.2, 1.3, 0.5 | **done 2026-09-29** - closed loop with adaptive pivots; arrivals: 12 pulses 594 -> 90 mm (80 mm marker), 14 pulses 667 -> 214 mm (160 mm marker) |
| 1.4a | ~~Re-tune homing on the trike~~ **done 2026-09-29** | - | pivot duty 50% (live slider), `PIVOT_S` 0.1 s ~6 deg, near step 0.1 s; first trike arrival 1109 -> 168 mm in 7 pulses |
| 1.5 | Bench lap demo | all above | drive a lap around a clutter-free zone using markers as waypoints |

## Tier 2E - the Eufy path (issue #1; revised 2026-09-28)

The Roomba turned out to be gone; Enoch has a **Eufy RoboVac 12** instead.
Decision: it becomes the house chassis, driven over **infrared** - the
11/11S/12 family is controlled by an IR remote, and ESPHome already drives
them with an IR LED and published Pronto codes. That keeps the vacuum's own
docking, charging, cliff and bumper behaviour intact (recharging solved, as
with the Roomba) at the cost of telemetry: no encoders or sensor readouts
come back over IR. The camera and brain ride on the lid; the brain steers by
vision. A later, deeper step taps the battery voltage and charging signal
inside the shell (also a known hack). Bench work (Tiers 0-1) is unchanged
and comes first.

| # | Item | Needs | Notes |
|---|---|---|---|
| 2E.1 | Health check | Enoch: does it run and dock-charge; is the remote around | a dead pack changes the plan (~$20-30 from budget) |
| 2E.2 | Codes | captured from the 12's own remote via the node's receiver - the 11S set shares the protocol and address prefix but **not** the command payloads, so the published codes didn't apply after all | done: 6 codes (forward/back/left/right/home/start-stop) in `firmware/eufy-ir.yaml` |
| 2E.3 | IR transmitter node | ESP32 devkit (Enoch has several) + IR LED on GPIO4 (100R), IR receiver on GPIO14; first flash by USB via the HA ESPHome dashboard, OTA after | flashed and online; 6 captured-code buttons + an 8 s test-burst button; drive path proven with a visible LED - **blocked on working IR LEDs** (on order) |
| 2E.4 | Brain backend | 2E.3 | same `drive`/`stop` tools; `status` limited to what the camera sees until 2E.6 |
| 2E.5 | Camera on the lid | mount, power | its own 3.7 V cell via the IP5306 at first; charged by USB |
| 2E.6 | Inside-the-shell telemetry (later) | open it up: battery voltage via divider, charging signal | published 11S wiring exists; gives low-battery and docked state |

## Tier 2 - recharging (Phase 2) - *now the Makeblock-only path; deferred unless the Eufy falls through*

| # | Item | Needs | Notes |
|---|---|---|---|
| 2.1 | Dock design | 3D print | a wedge the rover drives into, marker on its face, contacts at the end of travel |
| 2.2 | Charge contacts | pogo pins or copper strips (~$5-10 budget) | on the rover's nose and the dock |
| 2.3 | 3S charger + protection | 3S BMS/charger module (~$10-20 budget, unless inventory) | charging the pack in place, safely - the one piece of this project with real fire risk; design reviewed with Enoch before anything is wired |
| 2.4 | Auto-dock | 1.4, 2.1-2.3 | return-to-dock when `battery_voltage` drops below a threshold; confirm charging via voltage rise |
| 2.5 | Charge telemetry | 2.3 | charging state and current into the brain and HA |

## Tier 3 - robustness and efficiency

| # | Item | Needs | Notes |
|---|---|---|---|
| 3.1 | D1 Mini on the buck | wiring | removes ~0.5 W of linear-regulator heat |
| 3.2 | Camera sleep | firmware | deep-sleep or stream-off when nobody is watching; wake on demand |
| 3.2a | **Low-battery deep sleep** | firmware (rover + redcam) | below ~9.6 V with no command for 5 min, both ESPs deep-sleep and wake every 30 min to report voltage. The 9.3 V guard only stops *driving*; idle draw (~2.5 W: two ESPs + L298N regulator + buck) flattens a full pack in ~12 h, into cell-damage territory. Until this exists, Enoch switches the pack off when done (2026-09-29). |
| 3.2b | **Hardware low-voltage cutoff** | check whether the 18650 holder has a protection BMS; else a 3S BMS/LVC module (~$3-5 budget) | the real fix - the ESPs can't cut the regulators' quiescent draw. Goes inline with the pack switch. |
| 3.3 | Wheel odometry | 2 encoders or IR sensor + slotted disk (~$5-10 budget) | distance/heading without timing guesses; needed for anything beyond line-of-sight to a marker |
| 3.4 | Forward range / obstacle sensing | **Benewake TFMini + SparkFun Qwiic adapter (inventory)** | Plan: on the D1 Mini's I2C bus (3.3 V logic, D1/D2, next to the MCP23008) at address 0x10 - write `01 02 07`, read 7 bytes (valid flag, -, dist LSB/MSB in cm, strength LSB/MSB, range type). Power the TFMini's 5 V pin from the buck (peaks ~800 mA; the adapter's 3.3 V boost can't run it from the D1 Mini). Firmware guard: refuse forward when range < ~35 cm and an obstacle is ahead. **Minimum range is 30 cm**, so the camera keeps the last 20 cm of a homing approach; the LiDAR owns the lane. ESPHome has no built-in component - read it with an I2C lambda in a template sensor, or a small external component. |
| 3.4a | Brake on stop - **flashed 2026-09-29, switchable; A/B found no measurable effect on 0.25 s pulses, left off.** Retest at cruise (0.5 s+) when there's room | rover firmware (Enoch OK'd) | `stop` shorts the windings for ~150 ms (both IN pins on, EN high) before releasing - cuts the coast from ~8 cm to ~3 cm at cruise; matters most for the cliff stop |
| 3.4b | Rear cliff sensors | 2 more IR modules, MCP23008 pins 6/7 | reversing is blind today; near miss 2026-09-29 |
| 3.4c | Brain as a hosted service | container + MCP endpoint; placement via homelab-helper | for unattended runs and persistent state (Phase 3); the dev-VM script is a bench-phase arrangement |
| 3.5 | One-board consolidation | MCP23017 (inventory) + PCA9685 (~$3-5) | T-Camera drives the L298N over I2C; retire the D1 Mini; re-validate all safety behaviour |
| 3.6 | Brownout watch | - | log resets/WiFi drops; add the rail capacitor if they show |

## Tier 4 - roaming the house (Phase 3)

| # | Item | Needs | Notes |
|---|---|---|---|
| 4.1 | Floor-safe cliff sensing | cliff sensors tuned for flooring, stairs | different reflectance than the bench |
| 4.2 | Obstacle avoidance | 3.4 | furniture, cords, pets |
| 4.3 | Room awareness | markers per doorway or HA presence | "which room am I in" before any mapping |
| 4.4 | Waypoint navigation | 3.3, 4.3 | marker-to-marker routes between rooms |
| 4.5 | House rules | Enoch | where it may go, quiet hours, what to do when it meets an animal (stop, retreat) |

## Tier 5 - operations and fun

| # | Item | Notes |
|---|---|---|
| 5.1 | Brain as a hosted service | container on the cluster next to the other MCP servers; streamable HTTP |
| 5.2 | Rover dashboard view in HA | cameras, battery graph, motion/cliff state, last snapshot |
| 5.3 | Telemetry log | battery over time, drive history - feeds the journal's numbers |
| 5.4 | Patrol mode | scheduled lap with snapshots posted to HA |
| 5.5 | Voice | announcements through the Echo Pyramid ("docking", "low battery") |
| 5.6 | OLED face | the T-Camera's screen shows state/expressions instead of an IP address |

## Parts likely on hand (from the ESPHome configs and wirestudio's library)

Enoch pointed at wirestudio and the ESPHome repo as a view of what he has.
The catalog is a superset of the inventory, so each of these is a "check
the bin" rather than a certainty - but every one maps to a roadmap item and
would cost $0 if present:

| Part (catalog / in use) | Roadmap use |
|---|---|
| HC-SR04 ultrasonic (in use on one device), VL53L0X ToF | 3.4 obstacle sensing; 4.2 house obstacles |
| MPU6050 / BMI270 IMU (BMI270 in use) | heading hold for pivots; dead-reckoning between markers |
| INA219 current/voltage sensor | real battery state (current + voltage) on either rover; charge detection on the Eufy |
| PCA9685 16-ch PWM | 3.5 one-board consolidation (T-Camera drives the L298N over I2C) |
| Rotary encoder / pulse counter (both in use) | 3.3 wheel odometry on the Makeblock |
| LD2410 / LD2420 radar (10 devices use LD2420) | person/pet detection ahead - 4.5 house rules ("stop for animals") |
| WS2812B / NeoPixel (25 devices) | status ring on the rover; "eyes" |
| I2S mic + MAX98357A speaker (in use on the audio devices) | 5.5 voice on the robot itself, not just the Echo |
| HC-SR501 / RCWL-0516 motion | cheap "someone's here" wake-up for patrol mode |
| esp32-wrover-cam board profile | second camera (rear / downward for cliff verification) |

Bin check (2026-09-28): **HC-SR04, an IMU, and a PCA9685 are on hand**; no
wheel encoders that fit the Makeblock motors, so 3.3 odometry leans on the
IMU + timing (or a later optical encoder on a motor shaft). INA219 and
VL53L0X unconfirmed.
