# Bill of Materials & Shopping List

## Budget policy

If Enoch already has a part in inventory, he supplies it. Anything else this
project needs comes out of a standing **$100 budget** that Claude tracks here.
This budget only covers purchases Claude actually asks for - if Enoch chooses
to just go buy something himself (as with the IR sensors below), it doesn't
draw against it. Update the running total every time something *is* drawn
from it - don't let it go stale.

**Budget spent so far: $0.00 — remaining: $100.00** (as of 2026-09-28)

| Date | Item | Cost |
|---|---|---|
| 2026-09-28 | ~~Eufy RoboVac 12 replacement battery (Amazon)~~ ordered at $18.10, then cancelled the same evening - the vacuum's bottom power switch was off, the pack is fine | $0.00 |

## Bill of Materials (currently in the design)

Everything below is either installed on the rover or, for the camera, fixed
in place watching the workbench.

| Component | Qty | Role | Source | Status |
|---|---|---|---|---|
| Makeblock Starter Robot Kit (tank configuration) | 1 kit (chassis + 2 DC gear motors) | Drivetrain | Inventory | Installed |
| Wemos D1 Mini (ESP8266) | 1 | Main controller | Inventory | Installed |
| L298N dual H-bridge module | 1 | Motor driver; its onboard regulator also supplies the D1 Mini's 5V (~0.5A rating) | Inventory | Installed |
| MCP23008 I2C GPIO expander | 1 | Drives the L298N's 4 direction pins - added because the D1 Mini didn't have enough spare GPIO | Inventory | Installed |
| 18650 Li-ion cell | 3 (wired 3S) | Power, ~12.6V full / ~9.0V empty | Inventory | Installed |
| Resistor, 100kΩ + 27kΩ | 1 each | Battery-voltage divider: pack+ (L298N +12V terminal) -> junction -> A0, junction -> 27kΩ -> GND | Inventory | Installed - divider wired and calibrated (`multiply: 15.618`, reads 11.77V vs. a multimeter's 11.79V) |
| ONVIF camera, Thingino firmware ("camv3") | 1 | Fixed overhead workbench vision (not rover-mounted) | Inventory | Installed |
| ESP32-WROVER T-Camera | 1 | Spare board, earmarked for a possible future onboard FPV/vision upgrade | Inventory | Owned, not deployed |

## Shopping list (needed, not yet installed)

Firmware support for all of these is already written and waiting (see
`firmware/rover.yaml`) - driving is unaffected until they're wired in.

| Item | Qty | Purpose | Est. cost | Status |
|---|---|---|---|---|
| IR reflectance sensor module (e.g. TCRT5000-based) | 2 | Front-left / front-right cliff detection, into MCP23008 pins 4 and 5 | N/A - purchased directly by Enoch, not drawn from Claude's budget | **Ordered**, awaiting delivery/install |
| Electrolytic capacitor, 470-1000µF (contingency) | 1 | Only if brownouts/WiFi drops show up once the cliff sensors share the L298N's 5V rail with the radio | ~$1, would draw from budget if needed | Not needed unless that happens |

Nothing has drawn from Claude's $100 budget yet.

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
| Spare micro-USB cable, spliced | 1 | Buck converter 5V output -> T-Camera micro-USB power input (red = +5V, black = GND - verify by continuity; data wires left unconnected and insulated). Keeps the camera off its LiPo/JST charge circuit entirely | $0 - Enoch has spares | Decided, not yet built |
| 3.7V single-cell Li-ion pack (on the T-Camera's own JST battery connector) | 1 | Backup power: USB runs the board and charges this cell via the onboard IP5306; if the main pack dies, the camera keeps running so a stranded rover can still report where it is | $0 - Enoch has a spare | Planned - add only after the USB path is built and verified; measure the IP5306's charge-current draw on the main pack first (can reach ~2A) |
| 3D-printed camera mount (`hardware/camera-mount.scad`) | 1 | Pedestal cradle standing the T-Camera upright on the Makeblock plate (8mm M4 grid), lens/PIR/OLED forward, 10° down-tilt, open front, open gap under the board for the bottom-edge micro-USB plug, rear cable window | $0 (~17 g PETG, ~1h15m print) | Designed, sliced with placeholder dims (`hardware/prints/`); **waiting on caliper measurements of the board** before the real print |
| M4 x 8-10mm screws + nuts | 2 | Bolt the mount to the Makeblock plate | $0 - Makeblock kit hardware | On hand (kit) |

## Candidate: Eufy RoboVac 12 house chassis (issue #1)

| Item | Qty | Purpose | Source | Status |
|---|---|---|---|---|
| Eufy RoboVac 12 (+ its dock and IR remote) | 1 | House chassis with native docking/charging, cliff and bumper behaviour; driven by IR | Inventory | Confirmed working: it had simply been switched off at the bottom power switch |
| IR receiver module (VS1838B-type) | 1 | Captured the remote's codes; stays for adding buttons | Inventory | Wired, GPIO14 |
| IR LED (940 nm) + 100R resistor | 1 | Transmit codes to the vacuum's receiver from the lid | Inventory | Wired, GPIO4 |
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
