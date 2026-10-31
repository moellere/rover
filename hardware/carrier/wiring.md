# Grover wiring - as built before the DRV8871 swap (2026-10-31)

Recorded before Enoch disassembled the acrylic plate. The firmware pin map is
authoritative (`firmware/rover32.yaml`); the physical routing below comes from
his photos and his labels - **rows marked TODO are not yet confirmed** and must
not be treated as fact.

## Layout (from the photos)

- ESP32 devkit (38-pin WROOM-32D) on the half breadboard, 3V3/EN end to the
  right. Top header, right->left: 3V3, EN, VP, VN, 34, 35, 32, 33, 25, 26, 27, 14,
  12, GND, 13, D2, D3, CMD, 5V. Bottom header, left->right: CLK, D0, D1, 15, 2, 0,
  4, 16, 17, 5, 18, 19, GND, 21, RX, TX, 22, 23, GND.
- Battery divider resistor(s) on the top row near the 34/VN end.
- L298N at the rear, driven by a 6-wire jumper bundle (EN 17/16, direction
  22/23 and 19/18) - removed; 22/23/19/18 become the DRV8871s' IN1/IN2.
- LM2596 on the right, IN to the rear, OUT forward; OUT to the breadboard top rail.
- 4-pin housing at the breadboard's right end takes the TFMini cable
  (black/red/white/green) and a second cable - likely the TFMini and gyro I2C.
- A large electrolytic capacitor at the left - rail TODO.
- Off-board leads to the left: cliff sensors, LED chain, pack / dock.

## Connections

| Wire / label | From | To | Status |
|---|---|---|---|
| Cliff FL OUT | TCRT5000 FL | GPIO35 | pin certain; route TODO |
| Cliff FR OUT | TCRT5000 FR | GPIO32 | pin certain; route TODO |
| Cliff VCC / GND | both modules | 3.3 V or 5 V? / GND | **TODO - which rail** |
| TFMini SDA / SCL | TFMini | GPIO25 / GPIO26 | pins certain |
| TFMini 5V / GND | TFMini | 5 V rail / GND | TODO confirm |
| Gyro SDA / SCL | L3G4200D | GPIO21 / GPIO5 | pins certain |
| Gyro VIN / GND | L3G4200D | 3V3 / GND | TODO confirm |
| Battery sense | 100k / 27k divider from the 12 V rail | GPIO34 | values from the firmware notes; position TODO |
| LED data | GPIO4 -> 330 ohm | left headlight Din | certain; 10k pull-down fitted? TODO |
| LED 5V / GND | buck 5 V / GND | chain | TODO confirm |
| ESP32 5V / GND | buck OUT | devkit 5V pin / GND | TODO confirm |
| Buck IN | 12 V rail (pack + via BMS P+) / P- | LM2596 IN+/IN- | TODO confirm |
| Dock + | left pad | 1N5822 (band to the rail) -> 12 V rail | certain (10-26) |
| Dock - | right pad | P- | certain (10-26) |
| Large capacitor | ? | ? | **TODO** |

## After the swap (Enoch's layout, 10-31)

Driver tray bolted between the posts, drivers at the rear with terminals facing
back; the two Wago 221-415 at the FRONT between the front posts (next to the BMS
lead drop and the buck's IN; the acrylic's centre cut-out between them passes the
BMS leads); LM2596 on the tray's front standoffs, IN toward the Wagos. Mark the
Wagos +12 V / GND (identical parts); fuse holder inline on pack + before the +
Wago; 20-22 AWG from the Wagos back to the drivers' POWER terminals; make the
Wago connections before the cradle goes on (lever clearance under the 30 mm gap).

### Bus wiring (planned, see README)

12 V bus = two Wago 221-415 (+12 V, GND) fed from pack + through a 5 A blade
fuse and P-; feeds both DRV8871 POWER terminals, LM2596 IN, the divider; the
dock diode joins the + bus. DRV8871 left IN1/IN2 = GPIO22/23, right = GPIO19/18,
header GND to ESP32 GND, header VM unconnected. GPIO16/17 free.
