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
  breadboard; jumpers to the shield. Half breadboard: **400-point, 82 x 54 x
  9 mm** (Enoch, 10-26).
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

**v1 base = the Freenove Universal Breakout Board, FNK0101** (Amazon B0DT48T7CB,
Enoch has one). **Freenove's size diagram (10-26): board 87.63 x 83.19 mm, four
corner holes at 81 x 77 mm centres**, **3.4 mm (M3)** (Enoch, from Freenove's
design notes; ~3.3 mm in from the edges). Spacing calipered and confirmed (Enoch, 10-26). Devkit
sockets down the centre with eight LED driver chips between the rows; screw
terminals along both long edges; power jack, three regulator caps and the rail
jumpers on one short edge. 83 mm wide does not fit between the posts (64 mm) -
**it goes on the hinged plate above the battery**, power-jack edge to the rear,
terminal edges left/right: screw terminal per pin, a status LED per GPIO, switchable 5 V / 3.3 V
rails; fits ESP32 / Pico / Nano. Screw terminals don't shake loose (better than
Dupont for the cliff lines), and the pin LEDs make debugging visible. Checks
before it carries Grover:

1. **Are the status LEDs buffered?** *Yes - Freenove's design explanation
   (docs.freenove.com, fnk0101 "Design Explanation"): each pin feeds a buffer, no
   pull-up/down, so nothing loads the GPIO (fine for the GPIO34 ADC and the I2C
   lines too). An LED flickers on a floating pin - expected, not a fault. The edge
   test below is now a confirmation.* The cliff modules signal "cliff" as a HIGH
   pulled up through ~10 k; an unbuffered LED to ground on that pin would sag it to
   ~2 V, under the ESP32's ~2.5 V threshold - the pin would read "floor" at a real
   edge and the cliff guard would silently die. Look for a transistor/driver by the
   LEDs or an LED-disable jumper; then **test**: cliff sensor plugged in, Grover
   held over an edge, `front_left_cliff` must go true. Unbuffered -> cut or
   disable the LEDs on the cliff pins.
2. **Does the 38-pin WROOM-32D devkit fit its socket?**
3. ~~Hole spacing~~ - confirmed 81 x 77 mm, 3.4 mm holes (Enoch, 10-26).

### Layout decided (Enoch: "either works - reuse the battery tray, just moving it down", 10-26)

Bottom to top:

1. **Deck:** printed driver tray (2x DRV8871, LM2596) + **battery cradle v3
   lowered onto the deck** (its proven pack fit unchanged), replacing the L298N
   and the breadboard. **The pack lifts out of its pocket** (it never slid - an
   error in the first write-up, Enoch caught it): open the hinged plate, lift.
   What carries over from v3: the pocket and the BMS window exactly. What changes:
   (a) the BMS faces down through the floor window, so the lowered cradle needs
   short legs / a raised floor to clear the BMS and its leads (and that gap can be
   the cable run to the driver tray); (b) v3's pocket is shifted rearward on the
   post pattern (mass over mid-track, Enoch 10-19), so on the deck the rear posts
   would land inside the pocket - the new base must move those bolt points
   outboard, or the posts move. **Enoch: "scrap the existing plate if it doesn't
   work"** - the cradle base, the posts and their positions are all open. Keep
   only: the pocket/BMS-window geometry, the pack over mid-track, the camera's
   height and view, Makeblock-grid mounting. Likely result: one printed base
   (lowered cradle + driver tray + hinge posts) with the hinged plate above.
2. **The four 30 mm standoff posts** (64 x 96 mm, M4) stay, now spanning the battery.
3. **Hinged electronics plate** at the cradle's current height: FNK0101 on its
   81 x 77 mm M3 holes (power jack to the rear) + the half breadboard (82 x 54) in a
   pocket; **hinge on the two rear posts** (printed blocks on the post tops, M3 pin
   across), front edge resting on the front posts with M4 thumb screws; **a front
   perch for the camera mount** with the same +/-24 mm slots, so the camera keeps
   its height and view (homing and docking are tuned to it).

**Chassis, from the kit manual** (Makeblock Starter Robot Kit, Monoprice 13959,
Robot Tank build): two 0824-144 beams carry wheels and motors, joined by a short
cross beam; the deck is a Makeblock **Base Bracket B** (part 14403, acrylic; CC BY 4.0 model on Sketchfab, 1ab39585739d4af393f190fd28d4fc33 - needs a login to download) on an 0824-128 beam; the kit's
upper tier is a second BaseBracket on **M4 x 30 nylon studs** (six in the kit,
four used: our "30 mm posts" at 64 x 96). Battery cradle v3 replaced that upper
BaseBracket - so the redesign replaces the kit's second tier.

Footprint: board + breadboard need ~88 x 140 mm vs 64 x 96 mm between the posts,
so the plate overhangs - sideways (over the tracks) or fore-aft (toward the camera
mount).

**Proposed (Claude, 10-27, Enoch asked): bolt the printed base straight to the
chassis beams and retire the acrylic Base Bracket.** The 0824 beams' threaded
slot takes an M4 almost anywhere along them (no hole pattern to match), PETG on
aluminium beats brittle acrylic (cf. the 10-18 fall), and dropping a layer lowers
the battery and the hinged plate (dock-tower and overhead-camera clearance). What
moves: the dock pad plates/bars under the deck - to the base's underside or,
better, into the **nose bracket** (cliffs + contacts + TFMini + bumper), built at
the same time; the cliff mounts are on the front cross beam, unaffected until then.
**Frame geometry (kit specs + manual, 10-27):** 0824 beams are 8 x 24 mm 6061
extrusion, M4-threaded ends and slot (hole pitch: listings say both "12 holes in
96 mm" and "16 mm increments" - confirm from a photo). The two 0824-144 track
beams stand **on their sides** (24 tall, 8 wide); the 0824-096 cross beam lies
**flat** between them, bolted into their inside faces at the 5th hole from the
motor end (step 5) -> track beams ~96 mm apart inside. The Base Bracket rides on
an 0824-128 beam bolted onto the cross beam (2x M4 x 22, steps 8 and 11).

**Correction (Enoch, 10-27):** the cliff brackets and the dock pad plates bolt to
the acrylic Base Bracket, and the TFMini bracket to a metal plate (kit Plate 3x6)
that bolts to it - so retiring the acrylic moves everything at the front, and the
**nose bracket must be designed together with the base**, not after it.
(cliff-mount.scad's notes call its mounting face a "beam top, 24 deep, two hole
rows"; a front photo will settle which surface that is.)

**Motor mounts:** the motor plates stand up above the track beams; Enoch may be
able to rotate them to hang below, which would let the base lie flat across the
frame - otherwise cut-outs.

**Photos read (10-31, Enoch's front/side/ruler set; parallax ~+/-5 mm):** acrylic
deck top ~51 mm - matching cliff-mount.scad's measured 51 mm, so that part's
"beam top" is the acrylic, and the cliff mount, pad plates and TFMini bracket are
all defined relative to it in the scad files (the nose bracket reproduces them
from those numbers); track beams ~48-72 mm (on their sides); track top run
~85-90 mm, ~95 over the drive sprockets; motor plates top ~80 mm; TFMini lens
centre ~55 mm; battery cradle underside ~70 mm.

**Design direction from this:** bolt the printed base onto the **threaded slots
on the track beams' top edges** (~112 mm outside-to-outside, ~72 mm high) - the
FNK0101 (83 mm) and breadboard fit inside that width, nothing over the tracks.
The motor plates were the obstacle - **Enoch rotated them, now flush with the
beam tops (10-31)**, so the base lies flat on the beams. To confirm directly
(ruler on the part, not from a photo): outside width across the two beam tops;
beam-top height.

**Still needed (earlier list, now superseded by the above):** heights above the bench (track-beam top, cross-beam top, track
top run, motor-plate top); **before anything comes off**, one front-on photo at
bench level and one side-on with a ruler standing on the bench, showing the
acrylic with the cliff brackets, pad plates, TFMini plate and bumper in place -
the nose bracket must put each back exactly where it is (cliffs 65 mm ahead of the
axle, pads over the rollers, TFMini height/aim, bumper 10 mm ahead).

## Open questions for Enoch

1. **Cliff module supply:** 3V3 (as drafted) or 5 V today? At 5 V their outputs
   would exceed the ESP32's 3.3 V inputs - check what they're wired to now.
2. **PCB or perfboard first?** JLCPCB 5 boards ~$5 + $10-20 shipping (budget $66
   left), or hand-wire a perfboard from this schematic.
3. **Connector family:** do your crimp kits match 2.54 mm headers?
4. **Height under the cradle:** is 30 mm the clear height, or is something else
   (breadboard, wiring) taking space there today?
5. **The expansion shield:** two jumper-selected V rails (answered). Still
   fully specified (spacing calipered 10-26).
6. ~~Battery position~~ - decided: low (cradle v3 lowered), hinged plate above.
