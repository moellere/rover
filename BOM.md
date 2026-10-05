# Bill of Materials & Shopping List

## Budget policy

If Enoch already has a part in inventory, he supplies it. Anything else this
project needs comes out of a standing **$100 budget** that Claude tracks here.
This budget only covers purchases Claude actually asks for - if Enoch chooses
to just go buy something himself (as with the IR sensors below), it doesn't
draw against it. Update the running total every time something *is* drawn
from it - don't let it go stale.

**Budget spent so far: $3.29 — remaining: $96.71** (as of 2026-10-05)

| Date | Item | Cost |
|---|---|---|
| 2026-09-29 | GH1.25-to-Dupont 2.54 pre-crimped cable + connector kit (Amazon B087N4GY8Z) - Enoch bought it for inventory; Grover's share (one 4-pin TFMini lead) prorated by Enoch | $0.40 |
| 2026-09-29 | 3S 40A BMS protection/balance board (Gebildet, Amazon B0G6JQ8ZFN) - Enoch bought a 3-pack for $8.66 for inventory; one is Grover's, so 1/3 is charged here | $2.89 |
| 2026-09-28 | ~~Eufy RoboVac 12 replacement battery (Amazon)~~ ordered at $18.10, then cancelled the same evening - the vacuum's bottom power switch was off, the pack is fine | $0.00 |

## Bill of Materials - Grover (as built, 2026-10-05)

All from Enoch's inventory unless the Source column says otherwise.

| Component | Qty | Role | Source | Status |
|---|---|---|---|---|
| Makeblock Starter Robot Kit, **trike** (two driven wheels + trailing caster; tank until 2026-09-29) | 1 | Chassis and two DC gear motors | Inventory | Installed |
| ESP32 devkit (WROOM-32D, 38-pin) - `rover32` | 1 | Spinal cord (ESPHome): enables GPIO16/17, direction GPIO18/19/22/23, cliff GPIO35/32, TFMini I2C GPIO25/26, battery GPIO34 | Inventory (was the Eufy IR node's board) | Installed 2026-10-03 |
| L298N dual H-bridge | 1 | Motor driver | Inventory | Installed |
| 18650 Li-ion cells | 3 (3S) | Power, 12.6 V full / ~9 V empty | Inventory | Installed; one weak set retired 09-29, one bad cell found 10-04 - charge the set together and full |
| LM2596 buck, set to 5.2 V | 1 | 5 V for the ESP32 (VIN), the camera (spliced micro-USB) and the TFMini | Inventory | Installed |
| Resistors 100k + 27k | 1 each | Battery divider into GPIO34 (x4.664, calibrated 10-03 against a meter) | Inventory | Installed |
| Benewake TFMini (SparkFun SEN-14786) | 1 | Forward LiDAR: obstacle stop 50 cm, range for homing | Inventory | Installed on the printed bracket; direct GH1.25 lead, 5 V |
| GH1.25-to-Dupont lead (kit B087N4GY8Z) | 1 | TFMini direct connection (replaced the Qwiic boost chain and LD33V) | $0.40 prorated (budget) | Installed |
| TCRT5000 cliff modules (HW-870) | 2 | Front cliff detection, DO at 3.3 V | Enoch's purchase (not budget) | Installed on v4 mounts |
| TTGO T-Camera (`redcam`) | 1 | Rover camera | Inventory | Installed (printed cradle + adapter strip) |
| Printed parts (PETG): camera cradle, adapter strip, TFMini bracket, cliff mounts v4 (L+R) | - | see `hardware/README.md` | $0 | Installed |
| Printed caster skid (`hardware/caster-skid.scad`) + M5 bolt 25-30 mm + nut | 1 | Replaces the swivel caster (it yaws the rear on stops) | $0 | Staged to print |
| 3S BMS 40A board (1 of a 3-pack, B0G6JQ8ZFN) | 1 | Per-cell protection + balancing | $2.89 prorated (budget) | In hand, install deferred |
| Bench cameras: `camv3` (Thingino), `fishcam` (Wyze Pan v2, Thingino PTZ) | 2 | Watch the bench from behind and head-on | Inventory | Installed |

Retired: Wemos D1 Mini (now the bench IR test node `eufy-ir8266`), MCP23008
expander, LD33V regulator (TFMini now on 5 V directly), the Qwiic adapter
chain.

## Bill of Materials - the Eufy (house chassis)

| Component | Qty | Role | Source | Status |
|---|---|---|---|---|
| Eufy RoboVac 12 + dock + remote | 1 | House chassis: its own docking, charging, cliff and bumper behaviour | Inventory | Working |
| TTGO T-Camera V1.7 (`blackcam`) | 1 | Lid board: camera + IR (IO22), powered from its header 5 V | Inventory (spare) | Flashed and proven 2026-10-04; lid mounting/power next |
| 940 nm IR LED + NPN (2N2222/2N3904) + 1k base + 33R | 1 set | IR driver, ~105 mA, 2 m range | Inventory (LED/receiver kit) | Wired on blackcam |
| VS1838B 38 kHz receiver + Wemos D1 Mini (`eufy-ir8266`) | 1 | Bench tool for capturing/decoding remote frames | Inventory | In use |
| ESP32-C3 Super Mini (`eufy-ir-c3` config) | 1 | Spare IR node if needed | Inventory | Config ready, not flashed |

(The Roomba plan - mini-DIN plug, level shifter - is shelved; the Roomba was gone.)

## How to keep this current

- When a shopping-list item is actually acquired, move it into the BOM table
  with `Installed` status and log its real cost against the budget line above.
- When a part is swapped or removed, update its BOM row rather than deleting
  history - note what replaced it and why (and cross-reference the
  [journal](JOURNAL.md) entry that made the call).
- Anything that shows up in `rover.yaml` referencing a pin/sensor that isn't
  in this table yet is a bug in this file - fix it in the same change.
