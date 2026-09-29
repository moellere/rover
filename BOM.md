# Bill of Materials & Shopping List

## Budget policy

If Enoch already has a part in inventory, he supplies it. Anything else this
project needs comes out of a standing **$100 budget** that Claude tracks here.
This budget only covers purchases Claude actually asks for - if Enoch chooses
to just go buy something himself (as with the IR sensors below), it doesn't
draw against it. Update the running total every time something *is* drawn
from it - don't let it go stale.

**Budget spent so far: $2.89 — remaining: $97.11** (as of 2026-09-29)

| Date | Item | Cost |
|---|---|---|
| 2026-09-29 | 3S 40A BMS protection/balance board (Gebildet, Amazon B0G6JQ8ZFN) - Enoch bought a 3-pack for $8.66 for inventory; one is Grover's, so 1/3 is charged here | $2.89 |
| 2026-09-28 | ~~Eufy RoboVac 12 replacement battery (Amazon)~~ ordered at $18.10, then cancelled the same evening - the vacuum's bottom power switch was off, the pack is fine | $0.00 |

## Bill of Materials (currently in the design)

Everything below is either installed on the rover or, for the camera, fixed
in place watching the workbench.

| Component | Qty | Role | Source | Status |
|---|---|---|---|---|
| Makeblock Starter Robot Kit, **trike configuration** (two driven wheels + trailing caster; was the tank until 2026-09-29) | 1 kit (chassis + 2 DC gear motors) | Drivetrain | Inventory | Installed |
| Wemos D1 Mini (ESP8266) | 1 | Main controller | Inventory | Installed |
| L298N dual H-bridge module | 1 | Motor driver; its onboard regulator also supplies the D1 Mini's 5V (~0.5A rating) | Inventory | Installed |
| MCP23008 I2C GPIO expander | 1 | Drives the L298N's 4 direction pins - added because the D1 Mini didn't have enough spare GPIO | Inventory | Installed |
| 18650 Li-ion cell | 3 (wired 3S) | Power, ~12.6V full / ~9.0V empty | Inventory | Installed - pack swapped 2026-09-29 (the first set drained ~0.07 V/min at idle: weak cells); no BMS yet, so charge the set together and full |
| Resistor, 100kΩ + 27kΩ | 1 each | Battery-voltage divider: pack+ (L298N +12V terminal) -> junction -> A0, junction -> 27kΩ -> GND | Inventory | Installed - divider wired and calibrated (`multiply: 15.618`, reads 11.77V vs. a multimeter's 11.79V) |
| ONVIF camera, Thingino firmware ("camv3") | 1 | Fixed overhead workbench vision (not rover-mounted) | Inventory | Installed |
| Wyze Cam Pan v2, Thingino firmware ("fishcam") | 1 | `front` camera: across the bench, head-on view of the rover (since 2026-09-29) | Inventory | Installed |
| ESP32-WROVER T-Camera | 1 | Spare board, earmarked for a possible future onboard FPV/vision upgrade | Inventory | Owned, not deployed |

## Shopping list (needed, not yet installed)

Firmware support for all of these is already written and waiting (see
`firmware/rover.yaml`) - driving is unaffected until they're wired in.

| Item | Qty | Purpose | Est. cost | Status |
|---|---|---|---|---|
| IR reflectance sensor module (e.g. TCRT5000-based) | 2 | Front-left / front-right cliff detection, into MCP23008 pins 4 and 5 | N/A - purchased directly by Enoch, not drawn from Claude's budget | **Ordered**, awaiting delivery/install |
| 3S BMS protection/balance board, 40A (Gebildet 3-pack, Amazon B0G6JQ8ZFN) | 1 of 3 | Per-cell over-discharge/overcharge/short protection and top balancing for the 18650 pack - the firmware's 9.3 V guard only sees the pack total. Not a charger: still needs a 12.6 V CC/CV source. Wiring: B-, B1 (cell 1-2 junction), B2 (cell 2-3), B+ to the cells; P-/P+ to the load, with the voltage divider on the P side. The holder likely needs two balance taps soldered on - plan with Enoch first. Drill-style boards may ship latched off until charge voltage is applied once | $2.89 (1/3 of $8.66) | **Ordered** by Enoch 2026-09-29; specs to confirm from the board on arrival |
| Electrolytic capacitor, 470-1000µF (contingency) | 1 | Only if brownouts/WiFi drops show up once the cliff sensors share the L298N's 5V rail with the radio | ~$1, would draw from budget if needed | Not needed unless that happens |

First budget draw: the BMS board ($2.89), 2026-09-29.

## In progress: onboard camera (next milestone after cliff sensors)

Goal: mount an existing TTGO T-Camera (ESP32-WROVER-B, OV2640, hostname
`redcam`) on the rover so it has its own eyes, ahead of Phase 3 (house-wide
roaming, where the fixed workbench camera won't help). It already runs a
working ESPHome build - camera streaming (SXGA, ports 8080 stream / 8081
snapshot), a 0.96" OLED status display, a PIR motion sensor, and a restart
switch - currently deployed fixed/USB-powered elsewhere. See
[JOURNAL.md](JOURNAL.md) for the reasoning.

**Power plan (researched, not yet built):** the T-Camera has its own onboard
IP5306 power-management chip whose battery JST connector expects a
**single-cell 3.7V LiPo** - wiring the rover's 3S pack (9-12.6V) into that
connector would damage the charge IC. Safe path instead: buck converter ->
5.0V -> the board's **micro-USB input** (a documented, standard power path
for this board), not the battery connector. Buck input taps the L298N's
+12V/GND terminals (downstream of the rover's power switch, so the camera
powers off with the rover). Set and verify 5.0V output with a multimeter
before connecting the camera.

| Item | Qty | Purpose | Est. cost | Status |
|---|---|---|---|---|
| LM2596 adjustable buck converter (e.g. [Addicore LM2596](https://www.addicore.com/products/lm2596-step-down-adjustable-dc-dc-switching-buck-converter)) | 1 | Battery pack -> 5.0V for the camera, isolated from the L298N's already-tight 0.5A regulator | $0 - Enoch has these in inventory | Confirmed available; output needs setting to 5.0V and verifying with a multimeter before connecting |
| Spare micro-USB cable, spliced | 1 | Buck converter 5V output -> T-Camera micro-USB power input (identify VBUS/GND by continuity to the plug's outer pins; data wires unconnected). The board's 5-pin bottom connector does NOT accept 5 V power - USB is the only input | $0 - Enoch has spares | Soldered to the buck; **no voltage at the plug yet** - cable/splice being diagnosed |
| 3.7V single-cell Li-ion pack (on the T-Camera's own JST battery connector) | 1 | Backup power: USB runs the board and charges this cell via the onboard IP5306; if the main pack dies, the camera keeps running so a stranded rover can still report where it is | $0 - Enoch has a spare | Planned - add only after the USB path is built and verified; measure the IP5306's charge-current draw on the main pack first (can reach ~2A) |
| Benewake TFMini micro-LiDAR (SparkFun Qwiic SEN-14786) + SparkFun Qwiic Adapter (pass-through, no regulator) + Qwiic breadboard breakout | 1 | Forward range for homing stop distance and obstacle stop (roadmap 3.4) | Inventory | Firmware ready (guard boots off). Power plan 2026-09-29: Qwiic 3.3 V line from its own LD33V (below), **not** the D1 Mini's 3V3; SDA -> D2, SCL -> D1 alongside the MCP23008. Mount on the front beam, level |
| LD33V (LD1117V33) 3.3 V LDO, TO-220, + 10 uF out / in caps | 1 | Dedicated 3.3 V for the TFMini's Qwiic line, fed from the buck's 5 V - keeps the TFMini's boost off the D1 Mini's small regulator | Inventory (Enoch used it for the TFMini before) | Planned |
| Second 5 V lead from the buck | 1 | Buck OUT -> D1 Mini 5V/G; the D1 comes off the L298N's linear 5 V regulator (disconnect it - never two regulators on one rail) | Inventory | Planned, with the TFMini wiring |
| 3D-printed camera mount (`hardware/camera-mount.scad`) | 1 | Pedestal cradle standing the T-Camera upright on the Makeblock plate (8mm M4 grid), lens/PIR/OLED forward, 10° down-tilt, open front, open gap under the board for the bottom-edge micro-USB plug, rear cable window | $0 (~17 g PETG, ~1h15m print) | **v5 printed and in use** (`hardware/prints/camera-mount_v5`) |
| 3D-printed camera adapter strip (`hardware/camera-strip.scad`) | 1 | Bolts the cradle to the two front M4 standoffs (64 mm c-c) so the camera stops shifting on pulses | $0 (8.8 g PETG, 21 min) | **Printed 2026-09-29 and fitted** |
| M4 x 8-10mm screws + nuts + washers | 4 | Two into the standoffs, two through the cradle base into the strip | $0 - Makeblock kit hardware | Fitted |

## Candidate: Eufy RoboVac 12 house chassis (issue #1)

| Item | Qty | Purpose | Source | Status |
|---|---|---|---|---|
| Eufy RoboVac 12 (+ its dock and IR remote) | 1 | House chassis with native docking/charging, cliff and bumper behaviour; driven by IR | Inventory | Confirmed working: it had simply been switched off at the bottom power switch |
| IR receiver module (VS1838B-type) | 1 | Captured the remote's codes; stays for adding buttons | Inventory | Wired, GPIO14 |
| IR LED (940 nm) + 100R resistor | 1 | Transmit codes to the vacuum's receiver from the lid | Inventory - the two on hand turned out dead/wrong; replacements ordered by Enoch (not from Claude's budget) | Wired on IO4; drive path proven with a visible LED; awaiting working IR LEDs |
| ESP32-WROOM-32D devkit (`esp32dev`) | 1 | IR bridge node `eufy-ir` (`firmware/eufy-ir.yaml`) | Inventory | Flashed, online, 6 captured-code buttons |

(The Roomba plan - mini-DIN plug, level shifter - is shelved; the Roomba was gone.)

## Later: one-board consolidation (after visual homing)

Option Enoch raised, kept on file: drive the L298N from the T-Camera over its
I2C bus instead of the D1 Mini. Direction pins via an MCP23008/MCP23017
(both in inventory); the two PWM speed lines via a PCA9685 16-channel PWM
board (~$3-5, not in inventory - would draw from budget), or the PCA9685
alone for all six lines. Saves ~0.9 W idle (about a third more idle
runtime) and one WiFi client. Deferred until the safety firmware doesn't
need re-validating mid-phase. Cheaper interim win: power the D1 Mini from
the buck converter instead of the L298N's linear regulator (~0.5 W of heat).

## How to keep this current

- When a shopping-list item is actually acquired, move it into the BOM table
  with `Installed` status and log its real cost against the budget line above.
- When a part is swapped or removed, update its BOM row rather than deleting
  history - note what replaced it and why (and cross-reference the
  [journal](JOURNAL.md) entry that made the call).
- Anything that shows up in `rover.yaml` referencing a pin/sensor that isn't
  in this table yet is a bug in this file - fix it in the same change.
