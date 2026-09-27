# Bill of Materials & Shopping List

## Budget policy

If Enoch already has a part in inventory, he supplies it. Anything else this
project needs comes out of a standing **$100 budget** that Claude tracks here.
This budget only covers purchases Claude actually asks for - if Enoch chooses
to just go buy something himself (as with the IR sensors below), it doesn't
draw against it. Update the running total every time something *is* drawn
from it - don't let it go stale.

**Budget spent so far: $0.00 — remaining: $100.00** (as of 2026-09-27)

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
| 3D-printed camera mount | 1 | Attaches the T-Camera to the chassis at a useful angle | $0 (PETG on hand, printer available) | Not yet designed |

## How to keep this current

- When a shopping-list item is actually acquired, move it into the BOM table
  with `Installed` status and log its real cost against the budget line above.
- When a part is swapped or removed, update its BOM row rather than deleting
  history - note what replaced it and why (and cross-reference the
  [journal](JOURNAL.md) entry that made the call).
- Anything that shows up in `rover.yaml` referencing a pin/sensor that isn't
  in this table yet is a bug in this file - fix it in the same change.
