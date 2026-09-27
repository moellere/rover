# Roadmap

Claude's proposed sequence of capabilities, written 2026-09-28 (Fable 5.1)
at Enoch's request. Ordered by dependency, not by fun - though there's fun
in every tier. Budget notes assume the $100 pool in `BOM.md`; "inventory"
means Enoch already has it. Enoch reshapes this freely; it's a proposal.

## Tier 0 - finish the bench (Phase 1 close-out)

| # | Item | Needs | Why |
|---|---|---|---|
| 0.1 | Print and fit the camera mount | board measurements (Enoch), ~17 g PETG | everything visual depends on it |
| 0.2 | Camera on rover power | USB splice (Enoch), buck at 5.0 V | camera travels with the rover |
| 0.3 | Camera firmware for the rover role | camera mounted | fix mirror/flip for upright mounting; drop the stream to VGA for latency; keep 8081 snapshots; reflash (pre-authorized) |
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
| 1.4 | `home_to_marker` | 1.2, 1.3, 0.5 | closed loop: pivot until centred, approach in pulses, stop at range; abort on cliff/battery/lost marker |
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
| 2E.2 | Codes | ~~capture~~ Eufy's own T2108 remote listing covers 11S/12/15T/30, so the published 11S Pronto codes apply; the node still runs a receiver in dump mode as a fallback | done in `firmware/eufy-ir.yaml` |
| 2E.3 | IR transmitter node | ESP32 devkit (Enoch has several) + IR LED on GPIO4 (100R), IR receiver on GPIO14; first flash by USB via the HA ESPHome dashboard, OTA after | config written and compiled: 11 buttons (forward/back/left/right/auto/suction/start-stop/home/spot/walls/zigzag) |
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
| 3.3 | Wheel odometry | 2 encoders or IR sensor + slotted disk (~$5-10 budget) | distance/heading without timing guesses; needed for anything beyond line-of-sight to a marker |
| 3.4 | Bump/obstacle sensing | ultrasonic or ToF (~$3-8 budget) | stop before hitting the bench supply |
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
