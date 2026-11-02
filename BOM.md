# Bill of Materials & Shopping List

## Budget policy

If Enoch already has a part in inventory, he supplies it. Anything else this
project needs comes out of a standing **$100 budget** that Claude tracks here.
This budget only covers purchases Claude actually asks for - if Enoch chooses
to just go buy something himself (as with the IR sensors below), it doesn't
draw against it. Update the running total every time something *is* drawn
from it - don't let it go stale.

**Budget spent so far: $34.00 — remaining: $66.00** (as of 2026-10-26: + $14.26 DRV8871 3-pack)

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
| Parallax L3G4200D 3-axis gyro module | 1 | Yaw rate for on-board heading control (I2C 0x69 on GPIO21/5, 3V3) | Inventory | Wired and reading 2026-10-19 (SCL GPIO5). Board 22 x 20 mm, 8 pins in line along a 22 mm edge (breadboard SIP), one M2 hole 1.5 mm in from the centre of the opposite edge (Enoch, 10-31). From the top plate on it stands upright in the half breadboard, so the firmware's yaw axis moves off Z (verify with a test turn). (A GY-61 / ADXL335 analog accelerometer is also in inventory, deferred.) |
| TTGO T-Camera `redcam` (rover camera) | 1 | Eyes for homing | Inventory | Survived the 2026-10-18 fall (snapshot verified) |
| Makeblock caster bracket + printed skid | 1 | Rear support (trike) | Inventory / printed | **Bracket snapped, skid lost, 2026-10-18**; superseded by the tank rebuild (no rear support) |
| YD-ESP32-23 (ESP32-S3, 8 MB flash by boot probe, DevKitC-1 clone; fits the FNK0101) - `rover32` | 1 (several more in inventory) | Spinal cord (ESPHome); pin map in hardware/carrier/README.md | Inventory | Fitted 2026-11-01, replacing the WROOM-32D devkit (installed 10-03, destroyed 10-31: 12 V from a DRV8871 header VM pin on its 5V) |
| Sipeed M1s Dock (BL808, camera + NPU) | 1 | Candidate for on-board vision later (not ESPHome, not a spinal cord) | Inventory | Noted 2026-11-01 |
| DRV8871 H-bridge modules | 2 (+1 spare) | Motor drivers, PWM on IN1/IN2 (header VM = 12 V: leave unconnected) | see purchases | Installed 10-31; left IN1/IN2 swapped in firmware (motor leads reversed) |
| L298N dual H-bridge | 1 | Motor driver until 10-31 | Inventory | **Retired** (replaced by the DRV8871s) |
| 18650 Li-ion cells | 3 (3S) | Power, 12.6 V full / ~9 V empty | Inventory | Installed; one weak set retired 09-29, one bad cell found 10-04 - charge the set together and full |
| LM2596 buck, set to 5.2 V | 1 | 5 V for the ESP32 (VIN), the camera (spliced micro-USB) and the TFMini | Inventory | Installed. To do (10-24): 1N5822 Schottky in its output lead so USB can't back-feed it, buck raised to ~5.5 V - Enoch ordered a 30-pack ($5.99, his purchase, not budget), **received 10-26**. Buck-lead diode **deferred** until rover32 needs USB (until then: no USB with the pack connected); a second 1N5822 goes in the dock + lead (ROADMAP 2.3) |
| Bare 12 AWG solid copper (Romex ground), ~80 mm x 2 | 2 | Dock contact staples in the printed pad bars (replaces the copper tape and pogo pins: the Eufy base's sprung rollers are the spring side) | Inventory | Cut and fit pending (2026-10-25) |
| Dock-sense divider: 100k + 15k (+ optional 100 nF) | 1 set | Dock pad + (before D1) -> GPIO9: 'On dock' and the charging lights (11-01) | Inventory | Installed 11-01, calibrated |
| Panel-mount DC barrel jack 5.5/2.1 mm | 1 | Brick into the dock | Inventory if Enoch has one, else ~$1 | - |
| TalentCell 12.6 V 2 A Li-ion charger (5.5/2.1 mm barrel, charge LED) | 1 | Dock supply (Phase 2) - CC/CV for a 3S pack; the RD6018 in battery mode stood in for the first charge test | **$16.45 (budget)**, ordered 2026-10-24 (Amazon; Waveshare's $7 unit was ~$18 landed) | **Received 2026-10-26** |
| Resistors 100k + 27k | 1 each | Battery divider into GPIO8 on the S3 (x4.748, calibrated 11-02 off the dock; was GPIO34 x4.664 on the old board) | Inventory | Installed (a 47k sat in the 27k spot until 11-01) |
| Benewake TFMini (SparkFun SEN-14786) | 1 | Forward LiDAR: obstacle stop 50 cm, range for homing | Inventory | Installed on the printed bracket; direct GH1.25 lead, 5 V |
| GH1.25-to-Dupont lead (kit B087N4GY8Z) | 1 | TFMini direct connection (replaced the Qwiic boost chain and LD33V) | $0.40 prorated (budget) | Installed |
| TCRT5000 cliff modules (HW-870) | 2 | Front cliff detection, DO at 3.3 V | Enoch's purchase (not budget) | Installed on the wings ahead of the tracks; front-right swapped for a spare 11-02 (faulty) |
| TTGO T-Camera (`redcam`) | 1 | Rover camera | Inventory | On camera mount v7, on the top plate's front tab |
| Printed parts (PETG): driver tray v3, battery tray v2, top plate v2, camera mount v7, marker bracket, TFMini bracket, cliff mounts, headlight clip, dock ramp (white) | - | see `hardware/README.md` | $0 | Installed (carrier rework 10-31..11-02); battery cradle v3 retired |
| Printed caster skid (`hardware/caster-skid.scad`) + M5 bolt 25-30 mm + nut | 1 | Replaced the swivel caster on the trike | $0 | Printed and fitted 10-18, lost in the fall; superseded |
| 3S BMS 40A board (1 of a 3-pack, B0G6JQ8ZFN) | 1 | Per-cell protection + balancing | $2.89 prorated (budget) | Soldered to a new 3x18650 holder 2026-10-18 (Enoch); in the battery tray on the tread beams since 10-31 |
| Bench cameras: `benchcam` (Wyze Pan v2, Thingino PTZ, overhead; was `fishcam` until 2026-10-24), `camv3` (Thingino) | 2 | Overhead pose for steering and docking; a second view | Inventory | Installed |

Retired: Wemos D1 Mini (now the bench IR test node `eufy-ir8266`), MCP23008
expander, LD33V regulator (TFMini now on 5 V directly), the Qwiic adapter
chain.

## Inventory noted for later (Enoch's, not yet assigned)

| Part | Qty | Possible use |
|---|---|---|
| Raspberry Pi Pico 2 W (RP2350, WiFi) | a couple | Smart-dock controller (ROADMAP 6b) |
| 28BYJ-48 stepper + ULN2003 driver boards (several spares) | several | slow, precise positioning if ever needed |
| SG90 9 g micro servos (Enoch, 10-31) | 10 | **`redcam` pan mount** for Phase 3 dock search - better fit than the stepper: one PWM pin, absolute position, no homing |
| DRV8871 (one spare from the 3-pack) | 1 | spare motor driver |
| AI-Thinker ESP32-CAM | a couple | Spare cameras (too few free GPIOs to be the spinal cord) |
| WS2812B dots / strips, TCRT5000 (10-pack spares) | many | Lights; rear cliff sensors |

## Candidates (researched, not ordered)

| Part | Why | Price (checked 2026-10-26) | Status |
|---|---|---|---|
| DRV8871 H-bridge module, 3-pack (Teyleten Robot, Amazon B0DN66P9XW; listing checked: DRV8871, 3.6 A) | Replaces the L298N, which loses ~2-4 V inside itself - much of why the tracks needed 75 % duty to start; third board is a spare | **$14.26 incl. tax (budget)**, ordered 2026-10-26 | **Installed 2026-10-31** |
| INA219 current/voltage monitor (I2C) | Real charge current and "full" detection behind the diode (ROADMAP 2.5); on the second I2C bus, the TFMini keeps its own | ~$3-5 (not yet priced) | Ask Enoch's drawers first |

## Bill of Materials - the Eufy (house chassis)

| Component | Qty | Role | Source | Status |
|---|---|---|---|---|
| Eufy RoboVac 12 + dock + remote | 1 | House chassis: its own docking, charging, cliff and bumper behaviour | Inventory | Working |
| TTGO T-Camera V1.7 (`blackcam`) | 1 | Lid board: camera + IR (IO22), powered from its header 5 V | Inventory (spare) | Flashed and proven 2026-10-04; lid mounting/power next |
| 940 nm IR LED + NPN (2N2222/2N3904) + 1k base + 33R | 1 set | IR driver, ~105 mA, 2 m range | Inventory (LED/receiver kit) | Wired on blackcam |
| VS1838B 38 kHz receiver + Wemos D1 Mini (`eufy-ir8266`) | 1 | Bench tool for capturing/decoding remote frames | Inventory | In use |
| ESP32-C3 Super Mini (`eufy-ir-c3` config) | 1 | Spare IR node | Inventory | **Leaves the project 2026-10-26** - Enoch is reusing it for a pond fish feeder at Wyola; `firmware/eufy-ir.yaml` stays as the reference if an IR node is ever needed again |

(The Roomba plan - mini-DIN plug, level shifter - is shelved; the Roomba was gone.)

## How to keep this current

- When a shopping-list item is actually acquired, move it into the BOM table
  with `Installed` status and log its real cost against the budget line above.
- When a part is swapped or removed, update its BOM row rather than deleting
  history - note what replaced it and why (and cross-reference the
  [journal](JOURNAL.md) entry that made the call).
- Anything that shows up in `rover.yaml` referencing a pin/sensor that isn't
  in this table yet is a bug in this file - fix it in the same change.
