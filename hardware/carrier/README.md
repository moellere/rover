# Grover carrier board - v1 DRAFT (2026-10-26, for Enoch's review)

One board for Grover's electronics, replacing the breadboard and flying leads
("almost unmanageable today", Enoch). ROADMAP item 6a'. Nothing here is
ordered or built; this is the design to argue with.

**Where it lives:** the logic side is the wirestudio design `grover-carrier`
(ESP32-DevKitC-V4 38-pin, connectors, motor-driver sockets, battery divider,
LED data line; schematic exports to KiCad 8 cleanly). The power section below
doesn't fit wirestudio's board-rail model and is added in KiCad.

## Goals

- **Every peripheral on a keyed, removable connector**; nothing soldered to the MCU.
- **MCU in sockets** (2x 19-pin female headers): a later ESP32-S3 - or the Pico 2 W
  Enoch raised - is a new carrier, not a teardown. The spinal cord stays an ESP32
  for now (ROADMAP 6a').
- **Keep `rover32`'s proven pin map**, except the motor driver change below.

## Pin map (unchanged unless noted)

| Function | GPIO | Connector | Notes |
|---|---|---|---|
| Cliff front-left / front-right | 35 / 32 | J_CLIFF_FL / FR (3-pin: 3V3, GND, OUT) | 35 is input-only, no pull-up |
| Cliff rear-left / rear-right | 33 / 13 | J_CLIFF_RL / RR | reserved since 10-03, now populated |
| TFMini I2C (bus_b) | SDA 25 / SCL 26 | J_TFMINI (5V, GND, SDA, SCL) | TFMini alone on its bus, as decided 10-03 |
| Gyro L3G4200D (bus_c) | SDA 21 / SCL 5 | J_GYRO (3V3, GND, SDA, SCL) | GPIO5 is strapping; fine for an idle-high SCL |
| Battery divider | 34 | on board, 100k / 27k + 100 nF | sense from the pack + after the fuse |
| WS2812 chain | 4 | J_LED (5V, GND, DATA) | 330 ohm series, 10k pull-down, 470 uF at the connector |
| **Left motor DRV8871** | **IN1 22 / IN2 23** | socket + J_MOT_L (screw, 2) | **change:** PWM on IN1/IN2, no EN pin |
| **Right motor DRV8871** | **IN1 19 / IN2 18** | socket + J_MOT_R (screw, 2) | as above |
| Spare | 16, 17, 27, 14 | J_SPARE (3V3, GND, 16, 17, 27, 14) | 16/17 freed by the DRV8871 (were the L298N EN pins); 14 pulses at boot |

The DRV8871 swap needs a firmware change: the L298N drove direction on two pins
and speed on a PWM EN pin; the DRV8871 takes PWM on IN1 (forward) or IN2
(reverse) with the other low, and brakes with both high.

## Power section (added in KiCad)

```
 J_BATT (screw, 2) ── F1 5 A blade fuse ──┬── VBAT rail ── DRV8871 VM (both)
   pack + / P-                            ├── LM2596 IN+ (socket) ── OUT+ ──[D2 1N5822, optional]── 5V rail
                                          ├── vbat divider (GPIO34)
 J_DOCK (screw, 2) ──[D1 1N5822]──────────┘   (left pad +, band toward the rail; right pad -> GND/P-)
```

- **F1:** 5 A inline-blade fuse holder footprint (Enoch has one), the pack's only
  wiring protection upstream of the BMS.
- **D1:** the charge diode that already exists (bare pads dead off the dock).
- **D2:** the deferred buck-output diode, with a solder jumper across it; populate
  it when `rover32` needs USB with the pack connected.
- **LM2596:** module in a 4-pin socket (IN+, IN-, OUT+, OUT-), set to 5.2 V (5.5 V if
  D2 is fitted). 5V rail feeds the devkit's 5V pin, the TFMini, the LED chain.
- **Bulk capacitance:** 470-1000 uF on VBAT at the J_DOCK/J_BATT junction - the
  first suspect for the reboot on dock contact (the Reset Reason sensor will say).
- **GND:** one ground plane; P- of the BMS is the ground.

## Mechanical

- **Mounting:** four M4 holes (4.5 mm) at **64 x 96 mm centres** - the battery
  cradle's standoff posts (measured for `battery-cradle.scad`). The carrier sits at
  the foot of those posts on the deck, under the cradle; holes on the Makeblock
  8 mm grid. Board ~76 x 108 mm.
- **Height budget:** the posts are 30 mm; devkit in sockets ~22 mm, LM2596 ~15 mm,
  DRV8871 modules ~12 mm - fits, to be checked against the cradle's underside.
- **Connectors:** 2.54 mm headers (`pin_header` - most "JST-XH" kits are XH2.54
  clones) for signals; 5 mm screw terminals for battery, dock, motors.

## Enoch's layout input (2026-10-26) and where it points

- **The Makeblock baseplate is optional.** Today: L298N at the rear, breadboard at
  the front between the standoffs. With the L298N gone, a **printed electronics
  tray** (DRV8871 and buck sockets, cable channels) can replace it.
- **Battery:** stays removable. Claude's proposal: battery **low** (centre of
  gravity - see 10-18) sliding out the rear, electronics on a **hinged plate above**
  it (service access, and the ESP32 antenna on top). Pending Enoch.
- **One nose bracket** for cliff sensors, charge contacts, TFMini and the dock
  bumper, with wire channels - after the carrier, once cable routes are known.
- **Modular connectors grouped as GPIO + power + ground.** Enoch has a 38-pin
  ESP32 expansion shield (Amazon B0GX917MNR, G-V-S triple per GPIO). **v1 may be
  that shield + printed mounts instead of a custom PCB**; the custom PCB waits until
  the layout stops changing. Catch: most shields have one V rail (jumper 3.3 or
  5 V); we need both (TFMini, LEDs on 5 V; gyro, cliffs on 3.3 V).
- **Connectors:** XH2.54 latching (JST-XH clone pitch) for safety-relevant lines -
  cliff sensors, motors, power - since an unlatched Dupont can shake loose;
  Dupont acceptable elsewhere. 3-pin G-V-S per single-GPIO device; an I2C
  device spans two G-V-S triples on the shield (SDA's and SCL's), so it is
  individual leads anyway - one plug per device only arrives with a custom PCB.

### Follow-up (same day)

- **Shield + half breadboard on one printed plate** (Enoch): passives (LED
  resistor and cap, battery divider, anything experimental) live on the
  breadboard; jumpers to the shield. Needs the shield's outline/holes and the
  half breadboard measured (nominally ~82 x 55 mm).
- **The shield has two V rails, jumper-selected** (Enoch). His convention: 3.3 V
  on the devkit's 3V3-pin side, 5 V on its 5V-pin side. **No pin swap needed**
  (Enoch): with single Dupont leads a device's V wire can go to the other rail, so
  `rover32`'s proven pin map stays as is and only two leads cross - the TFMini's
  V to the 5 V rail (signals stay 25/26) and the gyro's V to the 3.3 V rail
  (signals stay 21/5). Colour-code them (red 5 V, orange 3.3 V). (A pin swap -
  gyro 25/26, TFMini 21/16 - was considered and dropped.)
- **GPIO expander:** not for anything safety-related, ever - the 10-03 MCP23008
  wedge froze motor direction and cliff inputs. 14 pins in use once the rear
  cliffs are in, ~4 spare (27, 14, 17, 5); new sensors go on I2C first (INA219 costs
  no pins); an expander, if it comes, carries only non-critical inputs (bumpers,
  buttons).

### The base board (Enoch, 2026-10-26)

**v1 base = the Freenove Universal Breakout Board** (Amazon B0DT48T7CB, Enoch
has one): screw terminal per pin, a status LED per GPIO, switchable 5 V / 3.3 V
rails; fits ESP32 / Pico / Nano. Screw terminals don't shake loose (better than
Dupont for the cliff lines), and the pin LEDs make debugging visible. Checks
before it carries Grover:

1. **Are the status LEDs buffered?** The cliff modules signal "cliff" as a HIGH
   pulled up through ~10 k; an unbuffered LED to ground on that pin would sag it to
   ~2 V, under the ESP32's ~2.5 V threshold - the pin would read "floor" at a real
   edge and the cliff guard would silently die. Look for a transistor/driver by the
   LEDs or an LED-disable jumper; then **test**: cliff sensor plugged in, Grover
   held over an edge, `front_left_cliff` must go true. Unbuffered -> cut or
   disable the LEDs on the cliff pins.
2. **Does the 38-pin WROOM-32D devkit fit its socket?**
3. Outline and mounting holes, for the plate (shield + half breadboard).

## Open questions for Enoch

1. **Cliff module supply:** 3V3 (as drafted) or 5 V today? At 5 V their outputs
   would exceed the ESP32's 3.3 V inputs - check what they're wired to now.
2. **PCB or perfboard first?** JLCPCB 5 boards ~$5 + $10-20 shipping (budget $66
   left), or hand-wire a perfboard from this schematic.
3. **Connector family:** do your crimp kits match 2.54 mm headers?
4. **Height under the cradle:** is 30 mm the clear height, or is something else
   (breadboard, wiring) taking space there today?
5. **The expansion shield:** two jumper-selected V rails (answered). Still
   needed: its outline and mounting holes.
6. **Battery low + hinged electronics plate**, or battery on top as now?
