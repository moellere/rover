# Bill of Materials & Shopping List

## Budget policy

If Enoch already has a part in inventory, he supplies it. Anything else this
project needs comes out of a standing **$100 budget** that Claude tracks here.
Update the running total below every time something is actually purchased -
don't let it go stale.

**Budget spent so far: $0.00 — remaining: $100.00** (as of 2026-09-27)

## Bill of Materials (currently in the design)

Everything below is either installed on the rover or, for the camera, fixed
in place watching the workbench.

| Component | Qty | Role | Source | Status |
|---|---|---|---|---|
| Makeblock tank-track chassis + DC gear motors | 1 set (2 motors) | Drivetrain | Inventory | Installed |
| Wemos D1 Mini (ESP8266) | 1 | Main controller | Inventory | Installed |
| L298N dual H-bridge module | 1 | Motor driver; its onboard regulator also supplies the D1 Mini's 5V (~0.5A rating) | Inventory | Installed |
| MCP23008 I2C GPIO expander | 1 | Drives the L298N's 4 direction pins - added because the D1 Mini didn't have enough spare GPIO | Inventory | Installed |
| 18650 Li-ion cell | 3 (wired 3S) | Power, ~12.6V full / ~9.0V empty | Inventory | Installed |
| ONVIF camera, Thingino firmware ("camv3") | 1 | Fixed overhead workbench vision (not rover-mounted) | Inventory | Installed |
| ESP32-WROVER T-Camera | 1 | Spare board, earmarked for a possible future onboard FPV/vision upgrade | Inventory | Owned, not deployed |

## Shopping list (needed, not yet confirmed acquired)

Firmware support for all of these is already written and waiting (see
`firmware/rover.yaml`) - driving is unaffected until they're wired in.

| Item | Qty | Purpose | Est. cost | Status |
|---|---|---|---|---|
| IR reflectance sensor module (e.g. TCRT5000-based) | 2 | Front-left / front-right cliff detection, into MCP23008 pins 4 and 5 | ~$2-6 total | Check inventory first |
| Resistor, 100kΩ | 1 | Battery-voltage divider, top (pack+ side) | <$0.50 | Check inventory first |
| Resistor, 27kΩ | 1 | Battery-voltage divider, bottom (A0/GND side) | <$0.50 | Check inventory first |
| Jumper wire | 1-2 | L298N +12V screw terminal -> divider -> D1 Mini A0 | <$1 | Check inventory first |
| Electrolytic capacitor, 470-1000µF (contingency) | 1 | Only if brownouts/WiFi drops show up once the cliff sensors share the L298N's 5V rail with the radio | ~$1 | Not needed unless that happens |

Estimated total if none of this is already on hand: **~$5-10** - well inside
the $100 budget. Nothing has been purchased yet.

## How to keep this current

- When a shopping-list item is actually acquired, move it into the BOM table
  with `Installed` status and log its real cost against the budget line above.
- When a part is swapped or removed, update its BOM row rather than deleting
  history - note what replaced it and why (and cross-reference the
  [journal](JOURNAL.md) entry that made the call).
- Anything that shows up in `rover.yaml` referencing a pin/sensor that isn't
  in this table yet is a bug in this file - fix it in the same change.
