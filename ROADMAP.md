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

## Tier 2R - the Roomba path (issue #1; decided 2026-09-28)

Enoch has an old Roomba with the Open Interface port. Decision: it becomes
the **house chassis** (Phase 3) and the way into Phase 2, conditional on
model and battery health; the Makeblock rover stays the bench platform.
The OI gives docking+charging (`Seek Dock`), 4 cliff sensors, bump and
wheel-drop, wheel encoders, and battery telemetry - which retires most of
Tier 2 and half of Tier 3 below for the house robot. Bench work (Tiers 0-1)
is unchanged and comes first.

| # | Item | Needs | Notes |
|---|---|---|---|
| 2R.1 | Identify and health-check | Enoch: model number, powers on, charges on dock | fixes OI version (57600 SCI on 4xx vs 115200 OI on 5xx+) and features |
| 2R.2 | Port cable | 7-pin mini-DIN plug/cable (inventory or ~$5) | pins 1-2 Vbat, 3 RXD, 4 TXD, 5 BRC/wake, 6-7 GND |
| 2R.3 | Controller + firmware | an ESP with a free UART; resistor divider on Roomba TX; LM2596 from Vbat | build on `dynodix/esphome-roomba` (SCI/OI external component) or `philpownall/ESPHomeRoomba` (MIT); the D1 Mini or a spare ESP32 |
| 2R.4 | Brain backend | 2R.3 | second platform behind the same `drive`/`status`/`stop` tools; `status` gains cliff x4, bump, encoders, charge state |
| 2R.5 | Dock/charge | 2R.3 | `Seek Dock` on low battery; confirm charge state from telemetry |
| 2R.6 | Camera on the Roomba | mount, power | the port's Vbat is behind a **200 mA PTC fuse** (~2.4 W after the buck) - fine for the ESP, marginal with a streaming camera; use the camera's 3.7 V backup cell or a direct battery tap |

## Tier 2 - recharging (Phase 2) - *now the Makeblock-only path; deferred unless the Roomba falls through*

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
