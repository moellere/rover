# Project Journal

This is the running log for the rover project: what changed, why, who decided
it, and which model did the work. It exists so that:

- Anyone (Enoch, a future Claude session, a different model entirely) can pick
  up exactly where things left off without re-deriving context.
- It's visible how much of this build is **Claude-driven** (identified,
  designed, or implemented without being asked for that specific thing) versus
  **Enoch-decided** (explicit direction, approval, or a choice only he could
  make - hardware in hand, budget, mission scope, etc.).

Each entry: date, model used, a summary of the guidance/instructions given
that session, what actually happened, and a Claude-driven/Enoch-decided
breakdown of the notable decisions. Newest entry on top.

---

## Current status (as of the latest entry below)

**Where things stand, 2026-10-05:**

- **Two robots, one brain.** **Grover** (Makeblock trike, bench platform)
  and a **Eufy RoboVac 12** (the house chassis, driven over IR). The
  brain (`brain/`, MCP server `rover-brain`) drives Grover; the Eufy is
  commanded through its lid board, `blackcam`.
- **Grover's spinal cord is an ESP32** (`rover32`, ESPHome) since
  2026-10-03 - no I/O expander, the TFMini alone on its own I2C bus.
  Guards in firmware: command watchdog, disconnect-stop, low-battery
  refusal (fixed today - see the week in review), cliff refusal, TFMini
  obstacle stop at 35 cm (incl. "was close, now too close to measure"),
  100 ms kick start, left-motor trim +6 %.
- **Sensors on Grover:** TFMini forward LiDAR (mounted, calibrated to
  1 cm), two TCRT5000 cliff sensors (v4 mounts put them on each tyre's
  centreline 65 mm ahead of the axle), rover camera `redcam`, plus two
  bench cameras (`camv3` behind, `fishcam` PTZ head-on).
- **Visual homing works** (`home_to_marker`, unattended arrivals to
  ~9-21 cm of an ArUco marker).
- **Grover drove through the house** on 10/04 - dining room, foyer,
  living room, to the kitchen doorway (~12-14 m) - and stopped itself at
  the edge of anything it couldn't clear (a dog, people, sun glare).
- **The Eufy is under our control.** Its IR protocol is decoded (the
  remote stamps the time into every command); `blackcam` (a T-Camera on
  the lid: camera + IR LED driver) drove it off the dock and sent it home.
- **Open:** a recurring hard swing at the start of some Grover pulses
  (kick start + battery-guard fix are the current suspects' remedies,
  untested); edge-stop test with the v4 cliff mounts; brain as a hosted
  service; Eufy battery/charging telemetry; BMS boards in hand, deferred.
- **Swing diagnosis (10/05, late):** battery-guard fix verified
  (`battery_ok=1`); TFMini guard verified (refuses forward; raised to
  50 cm and polled at 50 ms after a kicked pulse ended 15 cm from a box).
  Enoch saw the drift happen *after* a pulse stops, "like the right wheel
  freewheeling". Brake on vs off: both still turned ~20-30 deg on the
  stopping pulse; **with the swivel caster zip-tied straight, Grover
  stopped square**. Leading cause: the swivel caster twisting the rear on
  stops. Fix: Makeblock ball caster if in inventory, else a printed PETG
  fixed skid in the caster's holes (needs hole spacing and mount height). No ball caster in inventory, so: `hardware/caster-skid.scad` - a domed
  22 mm PETG puck, 36 mm tall, on one M5 bolt with a captive nut; staged.
  Also answered Enoch on the BMS: balance pads are taps only (no cutting
  between cells); the only re-route is the pack negative, which now goes
  to the board's 0V/B- while the load's negative moves to P-.
- **fishcam remounted overhead** (Enoch), looking straight down the bench -
  now the brain's `bench` camera; camv3 moves to the Eufy as its lid
  camera (Enoch's choice; the ESP32-C3 takes the IR job). First overhead
  test: two straight pulses, then a 20-25 deg yaw exactly where the front
  wheels met the **bench hatch's lip** (Enoch confirmed a slight lip; the
  black T-shape Claude first called its hinge is his solder fan).
  Revised picture of the swings: the swivel caster lets the rear swing,
  and bumps/seams (the hatch lip) or the stop transient start it. Fixes:
  the caster skid (printing) and a no-go/cross-square rule for the hatch
  in CLAUDE.md. Next: an ArUco marker taped on Grover's top so the
  overhead camera measures heading exactly (colour-segmenting the thin
  blue beam wasn't reliable).

Standing project rules live in [CLAUDE.md](CLAUDE.md) - read that first;
decisions and their reasoning are in the dated entries below. The
week-in-review entry right below summarises 09-29 .. 10-05; the dated
notes after it carry the detail (a few were appended out of order).

---

## 2026-09-29 .. 10-05 - Week in review: trike, TFMini, ESP32, cliff sensors, the house, the Eufy

**Models:** Claude Fable 5.1 through 10/04 afternoon, then **Claude Opus
5.5** (Fable's usage limit - the fallback CLAUDE.md names). Same
conversation throughout; the handoff was invisible to the work.

### Guidance from Enoch this week
- Grover named (09/29). "You tell me what you want to do next" - Claude
  picks milestones and moves through them without asking (recorded in
  CLAUDE.md); physical work and purchases still go through Enoch.
- Device permissions widened: the spinal cord, redcam, camv3, fishcam,
  the Eufy IR node, blackcam and Grover's ESP32 are Claude's to flash.
- Hardware realities he supplied: inventory (TFMini, ESP32 devkits,
  C3/S3/C6 minis, 940 nm LED/receiver kit, NPN transistors, a spare
  T-Camera that powers from its header), measurements (beam heights,
  wheel diameter, sensor board), and fixes (bad battery cell, swapped
  wires, a 3.3 V "GND", mis-wired receivers).
- Ground rules for the house run: no fall hazard; reversing/pivoting OK;
  "Taters" (the dog) will ignore you or bark; he watched the last stretch.

### What happened (threads, roughly in order)
1. **Trike + homing (09/29).** Tank tracks skidded on pivots, so the kit
   was rebuilt as a two-wheel trike with a trailing caster. Visual homing
   (closed loop: look, pivot toward the marker, step, re-look) arrived
   unattended three times. A reverse test put a wheel over the bench
   edge (caster flip drags the rear); new rule: reverse only in single
   short pulses, bench camera checked first.
2. **Brake-on-stop A/B.** Built a dynamic brake into every stop path;
   measured with the marker as a ruler - no measurable effect on short
   pulses, and it correlated with camera dropouts, so it became a switch
   that boots off.
3. **Battery.** A pack that sagged 2 V in 25 min idle was weak cells (not
   load) - proven by an idle drain log. 3S BMS boards bought for
   inventory (pad map recorded; deferred). One more bad cell found 10/04.
4. **Fishcam joined** as a head-on PTZ view; marker detection gained a
   CLAHE contrast retry for backlit frames.
5. **TFMini.** Bracket designed and printed; power plan reworked (Enoch
   spotted 5 V -> 3.3 V -> boost -> 5 V); direct GH1.25 lead. Bring-up was
   hard: every I2C read NACKed and the sensor wedged SCL low, taking the
   motor expander with it. Fix: repeated-start reads, 100 kHz, 20 ms
   clock-stretch limit. Calibrated (78 vs 77 cm); 35 cm obstacle guard.
6. **ESP32 spinal cord (`rover32`).** Because a wedged TFMini froze the
   motor controller, the spinal cord moved to an ESP32 devkit (flashed
   over WiFi onto the IR node's board), then - Enoch's suggestion - the
   MCP23008 expander was dropped entirely: direction and cliff pins went
   direct. Pins re-mapped twice for his layout. Battery sense
   recalibrated; motor channels and polarity fixed in config after a
   lifted test.
7. **Left-motor trim.** A slight drift was real; a `Left trim` number,
   calibrated on fishcam (0 -> 7 deg/pulse left, +10 -> 5 right, +6 ->
   straight).
8. **Cliff sensors (TCRT5000).** Mounts went through four versions with
   Enoch's fit checks: v1/v2 ribs didn't hold the board, v3 did (Claude
   rendered a three-view drawing for him to validate before printing),
   then Enoch pointed out the sensors sat inboard of the wheels - v4 puts
   each sensor on its tyre's centreline 65 mm ahead of the axle, PCB
   turned across the robot, slimmed to a spine + arm after his review.
   Powered at 3.3 V (DO is pulled to VCC; 5 V would exceed the ESP32).
9. **The Eufy's IR, the long fight.** Captures of the remote decoded into
   a frame `68 CMD HH MM 5C SUM` - **the remote stamps the current time
   into every command**, which is why last week's recorded codes were
   ignored. Transmitting failed for days: a mis-wired receiver, a 100 ohm
   resistor in the wrong place, a board "GND" at 3.3 V, receiver
   saturation, an ESP8266 software carrier the receivers never decoded -
   and, finally, **Claude's own bug**: the ESP32 receiver had been given
   all 512 RMT symbols, so the transmitter silently failed to initialise
   and every "send" since 10/02 emitted nothing. Enoch's meter (0 V on
   the pin) found it. With the RMT split, a hardware carrier, an NPN
   driver (~105 mA) and time-stamped frames: **Forward and Home worked,
   from 2 m.**
10. **blackcam - the Eufy's lid board.** A spare T-Camera now does camera
   and IR (LED driver on IO22; the OLED dropped so IO21 never moves and
   the I2C bus stays quiet). It drove the Eufy off its dock and back.
11. **Grover through the house (10/04).** Hardwood and rugs, short
   checked legs with a camera frame per pulse. Early on it met a wall at
   an angle - the TFMini went from "far" to "too close to measure" and
   neither the firmware nor Claude's loop treated that as an obstacle;
   both were fixed on the spot. Later it passed Taters on her bed,
   stopped for a dog that sat up in a doorway, and finished at the
   kitchen threshold because two people were standing ~1.5 m ahead (a
   rover at people's feet is a trip hazard).
12. **Today (10/05).** Temporary IR rig removed from rover32. A guard
   test was spoiled by another sudden swing, then by forward refusals at
   62-90 cm; logging the guard flags showed `battery_ok=0`: the port's
   battery filter published once per 2.5 min and latched "low" from a
   bad sample after every reboot. Rewritten (rolling 5 s, boot grace,
   re-arm on any reading > 9.6 V). Added a 100 ms full-power kick start
   so both wheels break stiction together - the leading suspect for the
   swings, since mechanics and wiring checked out.

### Decisions, 09-29 .. 10-05
| Decision | Who | Why |
|---|---|---|
| Trike instead of tank | Enoch raised it; Claude chose | track skid caused stiction and asymmetry |
| Brake-on-stop switchable, boots off | Claude | A/B showed no benefit on short pulses |
| TFMini direct (no Qwiic boost chain) | Enoch spotted it; Claude planned | removes three parts from the power path |
| Move the spinal cord to an ESP32 | Claude | a wedged I2C sensor must never freeze the motors |
| Drop the MCP23008 entirely | Enoch suggested; Claude agreed | no I2C left in the motor path |
| Cliff sensors at 3.3 V, DO to GPIO35/32 | Claude (correcting its own 5 V note) | ESP32 inputs are 3.3 V |
| Cliff mount v4 geometry (tyre centreline, 65 mm lead) | Enoch found the gap; Claude designed; Enoch trimmed it | angled approaches could put a wheel over first |
| Grover = bench platform; Eufy = Phases 2-3 | Claude | the Eufy already docks, charges, bumps; Grover is cheap to crash |
| Eufy IR on blackcam (camera + IR on one T-Camera, IO22) | Enoch offered the board; Claude chose the pin | one lid board, quiet I2C bus |
| Use the ESP32 hardware carrier, not the ESP8266 | Claude, from the evidence | software carrier never decoded |
| Stop rules for driving in the house (frame per pulse; stop on close range, invalid-after-close, weak WiFi; never toward people/animals) | Claude | the wall bump |
| Guard treats "close, then invalid" as an obstacle | Claude | the wall bump |
| Battery guard rewrite; kick start | Claude | latched-low guard; stiction asymmetry |
| Prints: drawings for validation before printing | Enoch's request, Claude adopted | caught two design errors before they cost a print |

### Lessons (for the next model, or a human)
- **Read the boot log for FAILED components before debugging hardware.**
  A day of IR testing went into a transmitter that never initialised.
- Instrument before guessing: logging the guard flags found the battery
  latch in one pulse; the idle drain log settled the battery question.
- Narrow-beam LiDAR misses anything off-centre and dark furniture returns
  weak; the camera check per pulse is not optional.
- A photo or a drawing before printing beats a reprint.

### Code and design this week (all in this repo unless noted)
- `brain/` (Python, ~640 lines): MCP server (`status`, `snapshot` for
  three cameras, `drive`, `find_marker`, `home_to_marker`, `set_brake`,
  `set_obstacle_stop`, `stop`), ESPHome API client, ArUco detection with
  per-camera calibration and CLAHE retry, the homing loop.
- Firmware (ESPHome; reference copies in `firmware/`, live configs in a
  private repo): `rover32.yaml` (spinal cord), `blackcam.yaml` (Eufy lid:
  camera + IR), `eufy-ir.yaml` / `eufy-ir8266` / `eufy-ir-c3` (IR test
  nodes), the retired `rover.yaml` (D1 Mini).
- Hardware (parametric OpenSCAD, printed through print-warden):
  `camera-mount`, `camera-strip`, `tfmini-bracket`, `cliff-mount` (v1-v4),
  plus drawings `cliff-mount-drawing.png`, `cliff-mount-v4-drawing.png`,
  `blackcam-ir-wiring.png`.
- ~80 commits this week, 121 in total.

### Open
1. Verify the battery-guard fix and the kick start on the bench, then the
   TFMini guard test against a box, then the cliff edge-stop with v4.
2. Eufy: lid mounting and power for blackcam; battery/charging telemetry
   (roadmap 2E.6); the brain learning to drive it.
3. Brain as a hosted service (roadmap 3.4c). BMS install (deferred).

---

## 2026-09-28 - Session 2: tooling, camera mount design, pipeline checks

**Model:** Claude Fable 5.1 (`claude-fable-5-1`) - third model on the
project, picked up from the docs plus the running conversation.

### Guidance from Enoch this session
- Proceed independently on the authorized work (camera firmware, mount design)
  and *define the next goal* after workbench mastery.
- The T-Camera (`redcam`) may be reflashed without asking - that device only.
- Print preferences: tree supports when needed, no brim.
- He can run sudo installs on the dev VM if asked.
- Signing off for the night; keep working within the rules but watch his
  Claude token budget (Fable has a limit; fallback is Opus 5.5 or waiting).

### What happened
- **Imagery confirmed:** pulled a 1280x1024 frame from the T-Camera's snapshot
  server (port 8081) - the board currently looks across a desk, tilted.
- **Research, sourced:** the Makeblock plate is an 8mm M4 grid in 2mm
  aluminum (Core Electronics / Studica listings). LilyGO's repo has the V1.7
  schematic and an official ESPHome config *without* mirror/flip - so the
  flips in the current config are from today's mounting, to be reset once
  it's upright on the rover. No 3D model or dimension drawing exists for the
  V1.7 anywhere found, hence the caliper request.
- **Firmware pipeline:** compiled the existing camera config on the current
  toolchain (esp-idf, clean apart from expected strapping-pin warnings) and
  OTA-flashed it; the camera came back serving frames. No config changes yet
  - orientation flags wait for mounting.
- **Printer found:** the Sidewinder X4 Plus is Klipper on an MKS Pi, reachable
  through Moonraker (read endpoints need no key); 300x300 bed, 0.4 nozzle.
- **Toolchain, no root:** OpenSCAD 2021.01 and OrcaSlicer 2.4.2 installed as
  extracted AppImages under `~/.local` via `scripts/install-tools.sh`
  (wrapper scripts, not symlinks - AppRun breaks otherwise). Orca has a
  built-in "Artillery Sidewinder X4 Plus 0.4 nozzle" profile and Generic
  PETG. It still needs GTK/WebKitGTK host libraries - bundling them
  user-side would mean ~300 packages, so the script documents one sudo
  `apt-get` line instead; Enoch offered to run it.
- **Mount designed:** `hardware/camera-mount.scad`, a parametric cradle with
  side rails, open front, USB window, 10° down-tilt, M4 slots on the 8mm
  grid. Rendered to STL and checked visually (matplotlib, since headless
  OpenSCAD can't make PNGs here): the first render leaned the wrong way
  (lens looking up) - fixed by rotating past vertical instead of short of
  it. Dimensions are placeholders pending measurement.

### Decisions
**Claude-driven:** the visual-homing goal proposal; OrcaSlicer over
PrusaSlicer (built-in X4 Plus profile; PrusaSlicer 2.9.6 has no Linux
build); the cradle-with-rails mount design and 10° tilt; flashing the
rebuilt firmware as a pipeline check.

**Enoch-decided:** the flash permission scope, print preferences, offering
sudo, and the token-budget constraint.

### Later the same night (Enoch briefly back)
- He ran the apt line - after a fix: `libgtk-3-0` is `libgtk-3-0t64` on this
  Ubuntu, and one unknown name makes apt-get abort the whole install.
  Orca then started headless.
- New constraint from Enoch: **the micro-USB (and 5-pin connector) are on the
  board's bottom edge.** Redesigned the cradle: it now floats on a pedestal
  with an open gap under the board for the plug and a rear cable window,
  resting on two corner tabs instead of a solid end-stop.
- Slicing pipeline built and proven: Orca's CLI rejects presets that
  `inherits` (duplicate-config error), so `scripts/orca_flatten_preset.py`
  flattens the X4 Plus machine / 0.20mm Standard process / Generic PETG
  filament chains into standalone JSON, with the house rules
  (`hardware/slicing/house-rules.json`: no brim, tree supports on auto)
  applied last. `hardware/slicing/slice.sh` does it in one command and
  extracts the G-code from the 3MF. Placeholder-dimension slice: **1h 14m,
  17.2 g PETG**, a few tree supports under the 10° lean. Files committed
  under `hardware/prints/` and uploaded to the printer's `rover/` folder
  (not started) at Enoch's request, labelled PLACEHOLDER-DIMS.
- Enoch asked about the brain and an MCP server. Recommendation given (not
  yet approved): both ESP boards stay ESPHome (spinal cord + eyes); the
  brain is an off-board Python service (OpenCV marker detection +
  aioesphomeapi driving) fronted by an MCP server with `snapshot`, `status`,
  bounded `drive`, later `home_to_marker` - the same shape as the boat's
  shore server. Firmware guards remain the authoritative safety layer.
- Confirmed for Enoch: the mount leans forward, camera 10° down (`tilt`).
- **Brain approved and built** (`brain/`): an MCP server (official MCP Python
  SDK, pinned to 1.x - 2.x renamed the server class the same week) with
  `status`, `snapshot(bench|rover)`, a hard-capped `drive` (<=1.0 s, 0.3 s
  gap, refused under 9.6 V or with a cliff active except backward), and
  `stop`. Hosts/keys come from `~/.rover-brain.env` via `brain/run.sh`, never
  the repo. Tested through a real MCP stdio client: tools list, both cameras
  return JPEGs; `status` correctly errors with the rover powered off.
  Registered with Claude Code at user scope as `rover-brain`.
- Board consolidation, discussed: Enoch asked whether the T-Camera replaces
  the D1 Mini. First answer was no (its GPIOs are all taken by the camera
  bus/OLED/PIR); Enoch pointed out the I2C expanders on hand (MCP23008, and
  16-pin MCP23017s), which makes it *possible* - direction pins via an
  expander, the two PWM lines via a PCA9685 (or PCA9685 alone). He also
  noted two boards drain the pack faster: ~0.9 W for the D1 Mini (half of
  it the L298N's linear regulator) vs ~1.5 W for the streaming camera -
  roughly 12 h idle with both, ~18 h with one, on a ~28 Wh pack. Decision:
  keep two boards through visual homing (the safety firmware is tested and
  the bench phase is about not falling off), then consolidate. Cheap wins
  first: feed the D1 Mini from the buck, sleep the camera when idle.

- Enoch signed off; measurements coming in the morning. Asked for a roadmap
  of future tasks/capabilities - written as `ROADMAP.md`. Also generated
  the printable homing marker and the brain's marker detector as groundwork
  (see the roadmap and `brain/markers.py`).

- **Issue #1 (Enoch): an old Roomba with the Open Interface port as a
  chassis.** Researched the OI spec and the open-source ESPHome components
  for it. Decision (Claude-driven, posted on the issue): adopt it as the
  house chassis and the path into Phase 2 - docking/charging, cliff x4,
  bump, encoders and battery telemetry come built in, retiring the dock/
  charger/BMS build - conditional on model and battery health; keep the
  Makeblock rover for the bench. Roadmap gained Tier 2R; BOM a candidate
  section. Waiting on Enoch for model number, health, and a mini-DIN plug.

- Test-fit print of the mini-DIN plug run overnight at Enoch's request (he
  authorized this one print), monitored through the printer camera with the
  workbench light switched on only for each shot: completed in 18 min,
  0.76 m of PETG, clean. The part is on the printer bed for him to test-fit
  in the Roomba's port.

- Morning news from Enoch: the plug test print's fit was off (key should be an
  inset groove, wire holes too small - both fixed in the file and shelved),
  and moot anyway - the Roomba had been given away. He has a **Eufy RoboVac
  12** instead. Researched it: the 11/11S/12 family is IR-remote controlled
  and ESPHome already drives them with Pronto codes; a deeper published hack
  reads battery/charging inside the shell. Decision (Claude-driven): the
  Eufy becomes the house chassis over IR, keeping its own docking/charging/
  cliff/bumper behaviour; roadmap Tier 2R rewritten as 2E. He also said the
  design-print-monitor loop working autonomously was "pretty spectacular".

- Enoch: the Eufy runs and dock-charges, the remote's on hand, IR
  receivers/LEDs in inventory, spare ESP32 devkits available. Verified via
  Eufy's own remote listing (one T2108 remote for 11S/12/15T/30) that the
  published 11S IR codes are the 12's. Built `eufy-ir.yaml`: an ESP32
  devkit IR bridge - transmitter on GPIO4 with the 11 remote functions as
  buttons, receiver on GPIO14 in dump mode as the fallback. Validates and
  compiles; needs one USB flash (HA's ESPHome dashboard), OTA after.

- IR node flashed by Enoch (ESP32-WROOM-32D devkit, factory image sent to
  him directly) and online. Captured his remote with the node's receiver:
  six clean codes (forward/back/left/right/home/start-stop). Finding: the
  RoboVac 12's remote shares the 11S protocol and 9-bit address prefix but
  its command payloads differ - the published 11S codes would not have
  worked, despite Eufy listing one remote for both. Rebuilt the node with
  the captured codes and OTA'd it (Enoch OK'd; recorded in CLAUDE.md).
  Vacuum-response test pending - the Eufy is also refusing to charge on its
  dock, which may mean a dead pack (~$20-30 if so).
- Camera mount: Enoch measured the board (28.0 x 68.0 x 1.27 mm, 6 mm rear
  components, USB centred) and clarified the USB lead runs straight down in
  line with the board, not bent backward. v3 adds a cable slot through the
  base aligned with a Makeblock plate hole. Sliced (1h 18m, 18 g), on the
  printer, awaiting his go.

- Camera mount v3 printed on Enoch's go: 80 min, 5.9 m of PETG, monitored
  at 4/31/57/86 % through the printer camera (light on only per shot) -
  clean throughout, tree supports did their job under the lean. Part is on
  the bed for him to de-support, test-fit the T-Camera, and bolt to the
  Makeblock plate.

- Enoch's photos of the v3 print with the board in it exposed a third
  problem beyond the two he named: full-length front lips can't work on
  this board (buttons at the edges, OLED nearly full-width). v4 fixed the
  outward-offset tabs/lips; v5 replaced the lips with 4.5 mm corner lips
  (upper ones chamfered for tilt-in). He judged v5 workable; printing.
- Power: the USB lead is soldered to the buck but there's only one, so it
  can't feed both boards. Recommendation given: feed the D1 Mini from the
  buck too (and disconnect it from the L298N's regulator - never parallel
  two regulators), via breadboard rails for the bench phase or a second
  soldered lead for anything that moves. Enoch's choice pending.
- The Eufy's pack is dead (dock lights up, vacuum never runs). Researched:
  14.4 V 2600 mAh replacements run ~$17 (eBay) to ~$20-25 (Amazon/Walmart).
  Proposed on the BOM shopping list against Claude's budget; awaiting OK.

- Plot twist: the Eufy's pack isn't dead - its bottom power switch was off.
  Enoch cancelled the battery order; the ledger is back to $0 spent. The IR
  drive test can happen as soon as it's charged.

- Camera mount v5 printed: 82 min, 6.6 m of PETG, clean at every check
  (6/38/69 %). On the bed for Enoch to de-support and test-fit - the corner
  lips and inside tabs are the things to verify this time.

- Eufy IR test, first live attempt: with the vacuum on the workbench and the
  node on its lid, Forward presses did nothing; the node's own receiver
  heard the LED (fragments only - receiver saturation at 2 cm, so loopback
  proves emission, not fidelity). Raised RMT buffers to 256 and set 3x
  repeats per press. Then, after Enoch repositioned node and vacuum, it
  **started reversing toward the bench edge** and he caught it. No job of
  mine was sending at the time. Unexplained; suspects are a label shift in
  the captured codes or the vacuum's own start-up behaviour. New rule in
  CLAUDE.md: the Eufy is tested on the floor only.

- Marker printed and placed on the bench; `find_marker` found id 0 live on
  the bench camera (48.6 px wide, dead centre) - first real detection.
- Rover powered on: brain `status` works (10.58 V idle, cliffs quiet), and a
  0.3 s backward pulse through the brain's client drove and stopped cleanly.
  Battery read 9.82 V right after the pulse - sagging near the brain's
  9.6 V refusal line; the pack needs a charge soon.
- T-Camera would **not** power from 5 V/GND on its bottom 5-pin connector;
  micro-USB is the only usable input. It's temporarily hanging from the
  pegboard on wall USB, looking down at the bench; its view is rotated by
  that mounting, so orientation flags wait for the bracket.
- The spliced USB lead delivers nothing at the plug despite ~5 V at the
  buck - diagnosis steps given (wire identification by continuity, broken
  conductor at the strain relief, polarity).

- Eufy on the floor: Home then Forward from the node did nothing. Loopback
  on the node's own receiver isn't proof of emission (38 kHz GPIO noise can
  couple in), and Enoch's phone saw no flicker (940 nm is nearly invisible
  to phones). Tried to see the LED with the bench camera: daylight mode
  blocks IR; forced night mode via Thingino's `json-imp.cgi` (cmd=daynight
  val=night|day; ir850/ir940 floods toggle likewise) - still nothing, but
  the open garage door floods the scene with daylight IR, so inconclusive.
  Next: electrical checks (multimeter across the LED during an 8 s test
  burst; wiring GPIO4 -> 100R -> anode), then a transistor driver if the
  LED is merely too dim.

- **Root cause found for the Eufy IR failure: the IR LEDs.** Two IR LEDs
  (swapped in turn) never showed on the night-mode bench camera; a visible
  LED in the same spot lit brightly on the 8 s test burst, so the node,
  IO4, the RMT transmitter and the captured codes are all fine. Possible
  mix-up with look-alike IR phototransistors (dark = receiver, clear =
  emitter). Enoch has new IR LEDs on order (his own purchase). The
  test-burst button stays in the firmware for the 30-second verification
  when they arrive; a transistor driver is the next step only if the
  vacuum ignores a working LED at distance.

- Bench camera calibrated for distance: Enoch measured lens-to-marker at
  66 in; the marker spans 50.7 px there, so the focal length is 1062 px
  (~84 deg horizontal FOV). The brain now holds a per-camera focal length
  (`BENCH_CAM_FOCAL_PX`, `ROVER_CAM_FOCAL_PX`) and `find_marker` reports
  distance - verified: 1676 mm back at 66 in.

- T-Camera mounted in the bracket on the rover and powered ("janky, but
  connected"). Its view is upright and un-mirrored as mounted, so the
  existing flip settings are right - no firmware change. The marker didn't
  decode at 50.75 in (too small: this lens is a fisheye), so Enoch moved it
  to 24 in: 57.3 px there -> ROVER_CAM_FOCAL_PX = 437 (~111 deg FOV).
  Verified 610 mm back at 24 in, bearing +10.2 deg. Generated a 160 mm
  id-1 marker page for longer range.

- **MILESTONE: visual homing works.** Wrote `brain/homing.py` - a closed
  loop (look, pivot toward the marker, step forward, settle, look again)
  with hard caps, lost-marker abort, and battery/cliff checks before every
  pulse - exposed as the `home_to_marker` MCP tool. First run stalled: a
  0.2 s pivot is below stiction on the bench (12 pulses, 1.3 deg total).
  Added adaptive pivot pulses (grow 1.5x when a pulse has no effect) and a
  6 deg centre tolerance. **Second run arrived: 12 pulses, from 594 mm and
  +4.9 deg to 90 mm and -4.4 deg, unattended.** The last 0.3 s step
  overshot the 200 mm stop, so steps inside 350 mm are now 0.15 s.
- Enoch found a Benewake TFMini micro-LiDAR with a Qwiic (I2C) adapter and
  breakout in inventory - added to the roadmap as the forward range sensor
  (better than the HC-SR04 for a precise stop distance and obstacle stop).

- Bench camera swap (handoff from the homelab-helper session, note in
  `handoffs/`, LAN addresses stripped on arrival): **agreed by Enoch,
  deferred until bench testing is done.** camv3 -> the PTZ "fishcam";
  camv3 goes to the printer. Rover side: new BENCH_CAM_HOST + password,
  one-time bench-cam recalibration, two PTZ presets ("bench", "wide").
  Future prints go through the print-warden MCP, which reuses this repo's
  slicing rules.
- **Homing against the 160 mm marker (id 1), later the same night** - a
  string of fixes from real runs:
  - Every other pulse looked ineffective because the camera's snapshot
    endpoint was serving frames up to 10 s old (`idle_framerate` was
    0.1 fps). Set it to 5 fps (needs `psram:`), reflashed, and `_look`
    now discards one frame and uses a second.
  - The loop ground against a mat edge/cables at 229 mm - added a stuck
    guard (three pulses with <0.5 deg / <15 mm change -> stop). A single
    1.0 s `backward` pulse freed it. Enoch then cleared the lane.
  - Still "stuck" at 325 mm with a clear lane: **left pivots do nothing
    at 0.2-0.6 s while right pivots bite at 0.25 s**; one 1.0 s left pulse
    turned it 12 deg (Enoch watched the left track move), then three more
    1.0 s left pulses did nothing at all. Loop changes first: pivot pulses
    adapt per direction, the cap is now 1.0 s (the server's max), and a
    no-effect pivot doesn't count toward "stuck" until its pulse has grown
    to the cap.
  - **Root cause: torque margin, not wiring.** Firmware drives both sides
    at the same duty, and with the rover lifted (Enoch's eyes) both tracks
    ran in sync forward and back. Under load, a tank pivot scrubs both
    tracks sideways and 75% duty was right at the edge - one direction
    got over it, the other didn't. With Enoch's OK, `left`/`right` now run
    at **100% duty** (forward/backward stay 75%). Result: 0.3 s pivots turn
    ~24 deg in *either* direction; initial pivot pulse dropped to 0.1 s.
  - **Second autonomous arrival, first on the 160 mm marker:** 667 mm ->
    214 mm in 14 pulses. The previous run had actually parked at 173 mm
    and 4.5 deg but reported "marker lost" - close in, the big marker
    overfills the T-Camera's frame and its border gets cropped. Arrival is
    now judged by lateral offset (<=30 mm) as well as bearing, and losing
    the marker right after a pulse inside 1.25x the stop distance counts
    as arrived.
  - **Chassis decision.** Enoch pointed out (not steering, just informing)
    that the Starter Robot Kit also builds as a two-motor trike with a
    trailing caster, and that it came with a Me Orion (Arduino + RJ25)
    board. Claude's call, Enoch proceeding: **rebuild as the trike** - the
    tank had to skid its tracks sideways to pivot, which is where all of
    tonight's stiction/asymmetry came from; wheels on an axle pivot at low
    duty with angle roughly proportional to pulse length, which is what
    homing wants. Same differential steering, so firmware and brain are
    unchanged; only pulse constants get re-tuned. **Keep the D1 Mini +
    ESPHome, skip the Orion** - it has no WiFi so the ESP stays in the loop
    anyway, and the tested watchdog/disconnect/cliff/battery firmware would
    have to be rewritten for no gain.
  - **Camera adapter strip** (`hardware/camera-strip.scad`) designed from
    Enoch's measurements: the two front M4 standoffs are 30 mm tall and
    measure 68.5 mm across the outer edges of their holes = 64 mm c-c (8
    grid units); slots cover 63-66 and are oversized per his request. The
    strip presents the v5 cradle's own M4 slot pair on top. Sliced (21 min,
    8.8 g). Enoch: "once you have designed it, if you're confident, you can
    print" - **printed 2026-09-29.** Fit check after the trike rebuild.
  - Enoch flagged that the bracket sits loosely and shifts on every jerky
    move, which corrupts bearings; he offered to measure the chassis
    posts so an adapter plate can bolt the mount down. Accepted -
    measurements requested (post spacing both axes, post type/diameter,
    height, which way is forward).

### The trike, same night (2026-09-29, late)

- Enoch rebuilt the chassis as the trike in about an hour (drive wheels in
  front, caster at the rear) and fitted the freshly printed camera strip -
  "worked great". Zip-tied the motor leads at his own suggestion.
- **Forward and backward came up inverted** on the new build (pivots were
  correct): rotating the motor mounts swaps sides *and* polarity. Caught it
  on the bench camera after one 0.1 s pulse moved the rover toward the near
  edge; no more pulses until fixed. Fix, with Enoch's OK: the four MCP23008
  motor pins and the two PWM pins are remapped in firmware.
- **Motor duty is now two live sliders** on the rover (`Drive duty` 75%,
  `Pivot duty` 50%), so tuning no longer needs a reflash. Needed at once:
  on the trike a 0.1 s pivot at 100% was ~30 deg. At 50%, 0.05 s is ~3 deg,
  0.1 s ~6 deg, left/right symmetric.
- **Third autonomous arrival, first on the trike: 1109 mm -> 168 mm in 7
  pulses, 35 s, final bearing -0.8 deg.** Four consecutive forward pulses
  held within 2 deg of centre. Near-range step cut to 0.1 s (the 0.15 s step
  overshot the 200 mm stop).
- redcam turned out to still be on ESPHome 2024.9.2: its config has never
  validated on 2026.x (`idle_framerate` max 1 fps; the camera's SCCB pins
  must be a separate `i2c:` bus; the OLED lambda used the Arduino `WiFi`
  object; `IPAddress::str()` removed in 2026.8). All fixed and **both
  firmwares are pre-built** (Enoch's suggestion: build while the pack is
  off, flash the moment it's back) - the rover's with brake-on-stop, the
  camera's on 2026.8.1. `_look` now retries
  transient camera errors and waits 1.2 s between its two frames.
- **Both flashed** once Enoch reinstalled the batteries: two OTA uploads,
  both OK; logs confirm 2026.8.1 with the pre-built compile stamps, the rover
  came back Stopped at 11.8 V and redcam serves frames on the new build.
- **Brake test aborted, camera lost.** First braked stop (0.3 s forward
  pulse, lane checked on the bench cam, marker 1082 mm at +19 deg) went fine
  mechanically - the caster flipped back to trailing and squared the rover
  up - but redcam dropped off WiFi within about a minute of it and had not
  returned 5 min later (no ping; HA unavailable from 09:24). The D1 Mini
  did not reset. Suspects: the brake's current transient disturbing the
  camera's supply, or the new 2026.8.1 camera build being fragile; homing
  runs on the old build survived dozens of unbraked stops. Needs a power
  cycle by hand; test paused until then.
- **Enoch power-cycled redcam** and widened the standing permission: the
  spinal cord, redcam, camv3 and fishcam are all Claude's to flash/modify
  for now. fishcam moved to the far side of the bench (head-on view).
- **Brake A/B.** Added a `Brake on stop` switch (default on; the script
  also now sets the pins to brake *before* EN goes to 100%, so there's no
  full-duty instant in the old direction) and flashed it. The brain got a
  `front` camera, a `set_brake` tool, and a CLAHE retry in marker detection
  - head-on at ~1 m the backlit marker's border merged into dark clutter
  and plain detection failed. Four 0.25 s forward pulses at 75% duty,
  marker distance as the ruler (median of 3 frames, ~+-6 mm):

  | Pulse | Brake | Travel |
  |---|---|---|
  | 1 | off | 128 mm |
  | 2 | on | 152 mm |
  | 3 | off | 153 mm |
  | 4 | on | 141 mm |

  Off averages 140 mm, on 146: pulse-to-pulse spread swamps any braking
  effect, so these gearmotors coast little at this speed (the "~8 cm
  coast" in the firmware comment was never measured). Camera trouble
  after 2 of 3 braked stops (the hang, then one HTTP 500 that cleared on
  retry) and 0 of 2 coasting ones - too few to call, but with no benefit
  shown the brake is left **off**. Retest at cruise when there's room.
  Rover left at 448 mm from the marker.
- **Pack draining fast at idle:** 11.7 V at ~09:20 -> 9.67 V at 09:45,
  falling ~0.07 V/min while Stopped (cameras + boards only). Far too fast
  for idle load - suspect a weak cell or a pack not fully charged. Asked
  Enoch to power off and charge, and to read per-cell voltages first if
  handy.
- **Enoch swapped in a different pack** (he has several). 30-min idle
  log: 11.84 -> 11.62 V, ~0.007 V/min and flattening - ten times slower
  than the old pack, so the old cells were the fault (11.7 V is only
  ~70% charge; the drain implied ~0.2 Ah usable). Neither pack went in
  at full charge (4.2 V/cell = 12.6 V).
- The brake switch came back **on** after the pack swap: ESP8266 switch
  state isn't persisted, so it fell to its RESTORE_DEFAULT_ON. Firmware
  now boots it off (`ALWAYS_OFF`), flashed and confirmed.
- Battery options discussed with Enoch (asked what's in inventory before
  pricing anything): a 3S BMS on matched 18650s (per-cell protection the
  pack-level 9.3 V guard can't give), an INA219 for current, matched cells
  charged full. Skipped for Grover: RC LiPo, USB-C PD bank + trigger,
  LiFePO4 - the Eufy carries the recharging mission.
- **Enoch ordered a 3-pack of 3S 40A BMS boards** ($8.66) for inventory;
  Claude took one for Grover, first budget draw ($2.89, $97.11 left).
  Wiring plan in BOM; soldering balance taps onto the holder to be
  discussed with Enoch when it arrives.
- **Enoch handed over milestone choice** ("you tell me what you want to do
  next") - recorded in CLAUDE.md. Claude picked the TFMini (roadmap 3.4).
- **TFMini, software side done before the hardware.** SparkFun's guide:
  the Qwiic TFMini's own cable carries 5 V directly (red 5V, black GND,
  white SDA, green SCL), so it runs off the buck and skips the adapter's
  3.3->5 V boost (the D1 Mini's regulator can't feed its ~800 mA peak);
  it reports invalid under 30 cm. Firmware: read at 10 Hz on the existing
  I2C bus (MCP23008 at 0x20, TFMini 0x10), `Front range` / strength /
  valid sensors, and an `Obstacle stop` guard (cm, 0 = off, boots off
  until verified) that refuses forward and stops a forward move inside the
  threshold. The guard holds through invalid frames (an object that got
  under 30 cm must not clear it) and, when enabled, treats a missing
  sensor as an obstacle. Flashed with no sensor attached: clean boot, no
  log spam, forward unaffected. Brain: range fields in `status`,
  `set_obstacle_stop(cm)` tool.
- Mount: the front blue beam above the motors (~5 cm off the bench) looks
  right from the fishcam view - low enough for small obstacles, and level
  keeps the 2.3 deg beam off the bench for a couple of metres. Needs the
  beam's hole layout and the sensor's mounting details from Enoch.
- **Power plan agreed with Enoch's inventory:** today the D1 Mini runs off
  the L298N's 5 V (linear) regulator and the camera off the buck. New: the
  D1 moves onto the buck's 5 V, and the TFMini's Qwiic 3.3 V line gets its
  own LD33V off that same 5 V (Enoch ran the TFMini this way before) - the
  SparkFun Qwiic Adapter is pass-through, the 3.3->5 V boost lives on the
  TFMini's cable board, so the D1's ~500 mA regulator would otherwise carry
  it. Enoch is doing the rework. He noted the LD33V build never had its
  10 uF caps - add them (LD1117 needs >= 10 uF on the output); the LD33V
  pinout is GND-OUT-IN, not a 7805's.
- Fishcam's PTZ works through HA's `onvif.ptz` (ContinuousMove; RelativeMove
  returns 500) - tilted down to inspect the parts on the bench, then back.
- **TFMini bracket designed** (`hardware/tfmini-bracket.scad`): ear holes
  from Benewake's TFmini-S drawing (Enoch's link; 2 x 2.35 mm at 36 mm
  c-c, same housing). Enoch: the beam's top face is free (the clear plate
  is set back), holes are top/bottom on the standard grid, not threaded,
  and the centre pair is taken by the bracket under the beam that joins
  the caster beam - so the part bolts through the next holes out (+/-12)
  with a relief pocket over the centre pair, and hangs the sensor in front
  of the beam at its mid-height. Staged via print-warden (job 010780c633,
  29 min, 7.9 g PETG); Enoch: "OK, print it" - started. Grover drove ~15 cm
  toward fishcam for a look at the beam and veered right (toward the long
  edge, ~13 cm clear); left there.
- **TFMini goes direct.** Enoch spotted the as-built chain was 5 V ->
  LD33V -> 3.3 V -> boost board -> 5 V. The TFMini takes 5 V and talks
  3.3 V I2C, so it can run straight off the buck with SDA/SCL on the D1
  Mini. He'd rather not cut the stock cable, so he ordered a GH1.25 ->
  Dupont 2.54 pre-crimped kit (Amazon B087N4GY8Z) for inventory; Grover's
  prorated share is $0.40 (budget: $3.29 spent, $96.71 left). The Qwiic
  chain + LD33V remains a stopgap until the kit arrives. Bracket printed
  meanwhile (print-warden: done, 36 min).

## 2026-10-01 .. 10-03 - TFMini bring-up, IR node debugging, BMS arrives

**Model:** Claude Fable 5.1. Enoch at the bench throughout, doing the
wiring; Claude flashing and reading logs. Auto mode was switched off
mid-way (Claude had flashed the IR node while Enoch was repositioning it,
which rolled the OTA back); rover, cameras and IR node stay Claude's to
flash, but Claude now says what it's about to do to a device Enoch has
in his hands.

### TFMini (done - reading)
- First attempts: with the TFMini's I2C wires on, the D1 Mini crawled
  (API handshake 5 s, status reads timing out) and the boot scan reported
  "SCL is held low" - no devices at all, MCP23008 included. First cause:
  the TFMini chain was unpowered (pack out, LD33V fed from the buck), an
  unpowered device clamps the bus. Then with the kit lead (direct 5 V,
  no Qwiic adapter) the scan found 0x10 and 0x20, but every transaction
  took 3 s: write NACKed, read timed out, and the sensor was left holding
  SCL low until a power cycle.
- Diagnosis by instrumenting the read (1 s poll, timing + raw bytes).
  Fix needed all three: **repeated-start** write/read (`write_readv`, as
  in SparkFun's example - a stop between command and read is refused),
  **100 kHz** (bus was 50), and an i2c `timeout: 20ms` (clock-stretch
  limit; the ESP8266 default is 230 us). Each try needed Enoch to
  power-cycle the rover because an OTA reboot doesn't reset the sensor.
- Result: reads in ~2 ms, valid frames, 77 cm at strength ~434 on the
  bench. Back to 10 Hz. The sensor was already in the printed bracket
  (fits; centred, level). **Calibration: 78 cm by TFMini vs 77 cm by
  tape to the marker** - within spec, no correction.
- **Guard verified:** set 35 cm, pulsed forward; at 30 cm the firmware
  logged "Forward blocked" and the motors stayed off. Guard now boots at
  35; `home_to_marker` relaxes it to 0 once the camera has the marker
  inside 35 cm (camera owns the last stretch) and restores it on exit,
  and reports "obstacle ahead at N cm" instead of grinding on a refusal.
- The ~90 deg left swing over three "forward" pulses was **not** the
  motors: both ran fine lifted (10 s test), and a repeat on the bench
  showed two straight pulses then a swing when, as Enoch saw, a wheel
  clipped an obstruction on the bench. The TFMini can't see low or
  off-axis objects (2.3 deg beam at ~5 cm height) - the lane check on the
  cameras stays mandatory.
- ...but a slight real drift remained (Enoch), and a later run swung
  hard left at the start of a pulse. Added a **Left trim** number
  (scales the left motor's duty on forward/backward) and calibrated it
  on fishcam: 0 -> ~7 deg/pulse left, +10 -> ~5 deg/pulse right, **+6
  -> straight** over three pulses; now the firmware default. Mechanical
  suspects for the hard swings (left wheel set screw, caster sitting
  sideways at pulse start) still worth a look.
- redcam came back on a new DHCP address; `~/.rover-brain.env` updated.
- Enoch: the IR node's ESP32 devkit is to become the new spinal cord
  (3.4d) - IR work stops. **Port done and compiled** (`rover32.yaml`,
  esp-idf): MCP23008 on bus_a (GPIO21/22), TFMini on its own bus_b
  (GPIO25/26, 100 kHz, 20 ms timeout), PWM on GPIO16/17 (ledc), battery
  divider straight into GPIO34 (12 dB attenuation, x4.704 - needs
  calibrating against a meter; the D1 Mini had an extra onboard divider).
  Device name `rover32` so both boards can coexist during the swap. First
  flash by USB from the HA ESPHome dashboard, then OTA. Wiring moves
  listed in README/BOM. Enoch asked whether to keep the MCP23008 now that
  pins aren't scarce: **dropped** - direction on GPIO18/19/23/27, front
  cliff on GPIO35/32, rear cliff reserved on 33/13 (36/39 are only
  labelled VP/VN on this devkit). No I2C left in the motor path at all;
  the TFMini is the only bus device.
- **rover32 brought up** (flashed OTA onto the IR node's board while it
  still ran eufy-ir - no USB needed). TFMini found on bus_b once SDA/SCL
  were the right way round (first "shifted by a pin", then swapped);
  battery sense needed its wire moved, then calibrated x4.664 (12.00 V
  read vs 11.90 V meter). Buck set to 5.198 V. Lifted motor test, then
  on the bench: forward ran backward and left pivoted right = both
  polarities flipped as wired -> fixed in config (swap fwd/rev pins per
  side; the channel ids also crossed to match the wiring). Verified by
  LiDAR range falling on forward and the marker swinging into view on a
  left pivot; Enoch confirmed. Brain now points at `rover32`; the D1 Mini
  is retired. TFMini 0xFFFF (no return) now counts as invalid.
- **Cliff sensors arrived** (HW-870 / TCRT5000, 31.5 x 14 mm, hole 7.5 mm
  from the pin end). Mounts designed (`hardware/cliff-mount.scad`, L
  bracket from the beam's end holes, sensor ~8 mm above the bench on a
  6 mm spacer boss) and printed on Enoch's "print them". Wire DO (not AO)
  to GPIO35/32, VCC 5 V.

## 2026-10-03 .. 10-04 - cliff mounts v3, IR node on the D1 Mini

**Model:** Claude Fable 5.1, then Claude Opus 5.5 from late 10/04 (Fable's
usage limit; the fallback CLAUDE.md names). Enoch at the bench.

- **Cliff mounts:** v1 ribs stopped short of the screw; v2 lengthened them
  along the shelf but they were only boss-high and never touched the
  board's edges (Enoch caught both). v3 ribs drop past the board on both
  sides; Claude rendered a three-view drawing (`hardware/cliff-mount-
  drawing.png`) for Enoch to validate before printing. Right v3 fits well;
  left v3 printed too (Enoch had said to skip it, but it had already
  started - cancelling is his gesture, not Claude's).
- **Battery:** one cell in the current pack is bad (Enoch found it after
  rover32 kept browning out). Swap that cell before the next long session.
- **IR, still unsolved.** The retired D1 Mini is now `eufy-ir8266` (D5
  receiver, D2 LED). Findings:
  - The first receiver was off-band or failing; a VS1838B (38 kHz)
    decodes the remote perfectly - so the remote is 38 kHz.
  - Our transmissions (8266 software carrier, ESP32 hardware carrier via
    rover32 on GPIO4, 36-60 kHz sweeps, 10 and 50 cm, bounce) only ever
    produce short fragments on that receiver - never a frame. A frame
    sent with NO carrier gives the same fragments, which means the
    receiver isn't seeing a 38 kHz-modulated light from our LED.
  - On the 8266, D2 averages 1.43 V and the 100 ohm drops 0.79 V during a
    burst, i.e. the pin toggles and the LED conducts. LEDs are kit
    940 nm clear emitters (Enoch confirmed).
  - A raw pin recorder on rover32 (GPIO33 jumpered to GPIO4) saw nothing
    during an 8 s burst - either the jumper or GPIO4's output; not
    resolved.
  - The remote's frame is `68 cmd XX YY ZZ sum`; the three middle bytes
    change between sessions (00 14, 00 07, 05 1B FF, 03 12 00) - looks
    like the remote's clock. Command bytes are stable.
  - Next: meter GPIO4 during a burst on rover32; swap to another emitter;
    if still fragments, buy a known-good IR transmitter module. rover32
    carries a temporary IR rig (TX GPIO4, raw RX GPIO33) to remove later.
- **IR SOLVED (10/04, 16:00): the Eufy drove forward on our command.**
  Three causes, all found the same afternoon:
  1. **Claude's bug:** on 10/02 the ESP32 receiver went to 512 RMT
     symbols to stop a crash - the chip only has 512 in total, so the
     transmitter failed to initialise ("out of RMT symbol memory",
     component FAILED) and every ESP32 send since logged "send" but put
     nothing on the pin. Enoch's meter on GPIO4 (0 V) found it. Fix: RX
     256 + TX 192. Lesson: read the boot log for FAILED components before
     debugging hardware.
  2. **The ESP8266's software carrier** never produced a decodable frame
     on a VS1838B; the ESP32's hardware (RMT) carrier did at once
     (`68 4F 00 07 FF BD` decoded back exactly). Use the ESP32.
  3. **The frame carries the remote's clock.** Format, confirmed against
     a fresh capture: `68 CMD HH MM 5C SUM`, HH = 12-hour hour, MM =
     minute (both binary), SUM = low byte of the first five. (The "5C"
     byte drifted between sessions too - 00/FF earlier - so treat it as
     "copy the latest capture".) Old captures with stale times were
     ignored. Forward (0x2C) stamped with the current time worked from
     ~3 cm off the bumper with the vacuum off the dock; Start/Stop was
     ambiguous. Command bytes: Fwd 2C, Back 7C, Left 3C, Right 6C, Home
     EF, Start/Stop 4F (+ 5C, 1D, AD, 5D unlabelled).
  - **Home (0xEF) also worked** (16:01) - the vacuum returned to its dock.
    Two commands now confirmed: Forward and Home.
  - Range: a 20 mA LED decoded with bit errors at 50 cm. **NPN driver
    added** (GPIO4 -> 1k -> base, emitter GND, 5 V -> 33 ohm -> LED ->
    collector, ~105 mA): loopback 18/24 frames clean, and **Forward worked
    from ~1 m** (16:16) **and from 2 m** (16:17). Test burst cut to 1 s so the 20 mA-rated LED
    isn't held at ~50 mA average. Next: find the max range, then move the
    IR to its own ESP32 node and strip the temporary rig off rover32.
- **IR's permanent home: blackcam** (Enoch's spare T-Camera V1.7, which
  powers from its bottom header unlike redcam). Flashed as the Eufy's lid
  board: camera + IR on IO22 (OLED dropped; IO21 untouched so no I2C
  START can happen on that bus), SNTP-stamped frames, buttons + an
  `eufy_command` action. Boot log clean (no FAILED). A C3 Super Mini
  config (`eufy-ir-c3`) is kept as a spare IR node.
- **Grover's direction set** (Claude, 2026-10-04): Grover becomes the
  bench test platform for the brain; the Eufy carries Phases 2-3.
- **Cliff sensors installed on Grover**, powered from **3.3 V** (DO is
  pulled up to VCC; 5 V would exceed the ESP32's inputs - corrected from
  the earlier 5 V note). GPIO35 front-left / GPIO32 front-right (wires
  were swapped at first; Enoch fixed). Both read clear on the bench and
  cliff when lifted. Edge-stop drive test next.
- **First floor run (dining room, hardwood).** Cliff sensors read clear on
  hardwood; ~22 cm per 0.3 s pulse, straight with the +6 % trim; TFMini
  tracked 3.9 -> 3.2 m. Then a 12-pulse scripted run toward the window
  ended **nose to a wall corner**: Grover drifted off line, met the wall
  at an angle, and the TFMini went from "far" straight to invalid (<30
  cm) - the firmware guard holds state on invalid readings, so it never
  tripped, and Claude's loop only checked valid readings, ran without a
  camera frame per pulse (weak WiFi, -82 dBm, made it slow) and timed out.
  A light bump at ~22 cm/pulse at most. **Fixes:** firmware now treats
  invalid-after-close (last good < 60 cm) as an obstacle; driving loops
  take a frame per pulse and stop on weak WiFi. One 0.3 s reverse
  (Enoch: safe) backed it to 53 cm. Cliff mounts v4 (sensor on the tyre
  centreline, 65 mm ahead of the axle) printing.
- **House run, continued** (Enoch: "keep going until you'd break one of
  the original rules"; reversing/pivoting allowed - no fall hazard; light
  on; Taters elsewhere). Short legs, a camera frame per pulse, stops on
  close range, invalid-after-close, cliff or weak WiFi. Dining room ->
  past the sideboard -> foyer, ~4-5 m. Findings: the TFMini's 2.3 deg beam
  misses anything off-centre (caught a sideboard leg at 52 cm; pushed
  into an orange object at the front-left corner it never saw); dark
  furniture returns weak/invalid readings; ~1-2 deg/pulse left drift on
  hardwood even with the +6 % trim. Stop rule refined: invalid readings
  stop only when the last good one was < 150 cm. **Stopped at the
  living-room opening:** Taters' position unknown and a lying dog is low
  and soft - the TFMini and a rover-height camera can't clear that, which
  would risk the "never harm an animal" rule. House roaming stays the
  Eufy's job (bumpers); Grover remains the bench platform.
- Enoch: Taters ignores robots (lies on her bed, maybe barks) - so the
  run went on into the living room (hardwood and rugs fine; rug edges
  climbed; cliff sensors read rugs as floor). Stopped by sun glare toward
  the French doors (camera blinded, and sunlight affects the TCRT5000s)
  and parked at the TV stand. Battery 11.3 V after ~10 m of driving.
- **blackcam drove the Eufy.** Enoch wired the NPN driver to its header
  (diagram `hardware/blackcam-ir-wiring.png`) and aimed it from above; a
  single `eufy_command(0x7C)` (Backward, SNTP time-stamped) backed the
  Eufy off its dock, seen through blackcam itself. Lid board proven:
  camera + IR on one T-Camera. (Claude first proposed Forward from a
  flipped camera view - Enoch corrected it; the T-Camera image is
  mirrored/flipped, mind the orientation.)
- blackcam also sent **Home**: the Eufy re-docked (charging light on).
- Grover to the kitchen: Enoch gave the route (slight right, forward,
  left into the doorway). Passed Taters on her bed at >1 m; a dog sitting
  up inside the doorway stopped Claude until Enoch said he was watching;
  ended on the doormat at the kitchen threshold and stopped there - two
  people standing ~1.5 m ahead, and a rover at their feet is a trip
  hazard. Whole run ~12-14 m, dining room -> foyer -> living room ->
  kitchen doorway, battery still 11.3 V.
- Back on the bench: rover32's temporary IR rig removed (IR lives on
  blackcam). **Guard test aborted:** aimed at a cardboard box, Grover
  swung ~90 deg on the second pulse (camv3 + rover cam). That is the
  fourth sudden swing at a pulse start (bench x2, floor x1, now), with
  the wheels mechanically fine and both motors fine lifted - suspect an
  intermittent connection on one motor channel (GPIO16/17/18/19/22/23
  jumpers, L298N terminals, motor connectors). Driving paused until
  checked. Cliff mount v4: right printed, left printing.
- **Lesson/risk:** on a shared bus a stuck TFMini takes the MCP23008
  (motor direction pins, cliff inputs) with it. Decision: move the spinal
  cord to an ESP32 (two hardware I2C controllers -> TFMini on its own
  bus; spare UARTs) - roadmap item, not blocking.

### IR node (open)
- New IR LED and receiver installed. Receiver first sprayed ~25 frames/s:
  Enoch had a 100 ohm from OUT to GND (Claude's diagram was misread - the
  resistor is the LED's); then dead quiet. Rewired correctly, it decodes
  the remote cleanly, and near the dock it decodes the dock's beacon
  (NEC-style 9/4.5 ms header, payload 0xD6, ~5/s).
- Fresh captures vs the 09/28 set revealed the **frame format**: 6 bytes
  `68 cmd 00 FIELD FF sum`, sum = low byte of the first five. FIELD was
  0x13-0x14 on 09/28 and 0x07 on 10/02 on every button - a slow clock or
  counter. Command bytes: Fwd 2C, Back 7C, Left 3C, Right 6C, Home EF,
  Start/Stop 4F (two unlabelled buttons today: AD, 5D).
- Firmware: `eufy_send(command, field, carrier_hz)` builds any frame with
  the checksum; carrier_hz <0 generates the 38 kHz carrier in software.
  Receiver `rmt_symbols: 512` after a crash (log ring buffer, from the
  receiver loop) on the first loopback frame.
- **Transmitter still unproven:** nothing it sends is decoded by the
  node's own receiver (direct aim, bounce, 30-56 kHz sweep, software
  carrier, bigger LED), and the vacuum ignored Start/Stop in all four
  forms (hw/sw carrier x field 07/14). The dock beacon floods the
  receiver whenever the node is near the dock, so most loopbacks were
  contaminated. Next: loopback in another room; if still nothing,
  scope the LED pin.
- OTA gotcha: the ESP32 rolls back if it resets within 60 s of a new
  image - unplugging the node right after a flash undid it twice.

### BMS
- 3S 40A boards arrived; pad map in BOM. Deferred (Enoch: rover first).
- **Near miss, backing up.** Enoch asked for a test reverse toward the bench
  camera. Done in 0.3 s pulses with the marker as odometry and a stop at a
  known-safe distance - but the caster flipping on direction change dragged
  the rear sideways each pulse (+8, +11.5 deg drift), the third pulse
  turned the rover ~45 deg and lost the marker (the loop stopped on that,
  as designed), and it ended **with one wheel over the right-hand bench
  edge** - Enoch called it from the bench and lifted it back. Claude's
  error, precisely: the "look between pulses" used only the rover camera,
  which faces away from the direction of travel; marker distance measured
  how far back it had gone and nothing about the rear drifting sideways.
  The bench camera was the only sensor covering the space behind it and
  the script didn't consult it until the end. Rule added to `CLAUDE.md`:
  reverse is single short pulses with a bench-camera look before each one;
  the caster makes it unpredictable and there are no rear cliff sensors.
- **The rover is named Grover.** Enoch called Claude "the big blue Grover
  of your rover" (a Chef John-style rhyme); Claude read it as Sesame
  Street's Grover, Enoch liked the near/far fit, and the blue Makeblock
  rails sealed it.
- Power management, on Enoch's question before bed: firmware only refuses to
  drive under 9.3 V; idle draw still flattens a pack. For now he switches the
  pack off; deep-sleep and a hardware LVC are on the roadmap (3.2a/3.2b).

### Decisions, 2026-09-29 (Fable 5.1)

| Decision | Who | Why |
|---|---|---|
| Pivot at 100% motor duty (forward/backward stay 75%) | Claude proposed, Enoch approved the reflash | left pivots stalled under load at 75%; unloaded the tracks ran in sync, so it was torque margin, not wiring |
| Homing "arrived" = within the stop distance **and** either bearing <= 6 deg or lateral offset <= 30 mm; a lost marker right after a pulse at close range counts as arrived | Claude | at 170 mm the 160 mm marker overfills the frame; the loop was parking correctly and reporting failure |
| Per-direction adaptive pivot pulses, 1.0 s cap, stuck guard only after a pivot has maxed out | Claude | left and right needed different pulse lengths; the guard was quitting before the pulse had grown |
| Stop distance for the big marker stays 200 mm | Claude | the camera keeps the full marker in frame at ~215 mm; closer than that is the TFMini's job later |
| **Rebuild the chassis as the trike** (two motors + trailing caster) instead of tank tracks | Enoch raised the option without steering; Claude chose; Enoch is doing the rebuild | tank pivots skid the tracks sideways - the source of tonight's stiction and asymmetry; differential steering is unchanged so firmware and brain carry over |
| **Keep the D1 Mini + ESPHome; don't move to the kit's Me Orion board** | Enoch offered; Claude declined | no WiFi on the Orion, so the ESP stays anyway; the tested safety firmware would have to be rewritten for no gain |
| Adapter **strip** across the two front standoffs, not a full plate | Enoch asked which; Claude chose the strip | two posts 64 mm apart fully constrain a 30 g camera; a full plate waits until the TFMini and cliff sensors need mounting on the trike layout |
| Standoff slots oversized (4.5 mm, slotted 63-66 mm c-c) | Enoch's request | measurement was across hole edges; screw heads cover the play |
| Strip printed tonight without a fit check on the trike | Enoch: "if you're confident, you can print" | flat 20-minute part, 8.8 g; low cost to reprint if the trike moves the posts |
| Prints go through the print-warden, not the printer API | Enoch (and the homelab-helper session) | one gate for slicing, start permission, and monitoring; rule added to `CLAUDE.md` |
| Bench camera swap to the PTZ still deferred | Enoch, earlier tonight | finish testing on the current calibration first |
| Rewriting public git history to purge the earlier LAN-IP leak | **open - Enoch's call** | the tip is clean; a force-push touches a public repo, so not done without his say-so |

### Open for next session
1. Enoch: measure the board (six numbers in the `.scad` header), build the
   USB splice, print the marker page (`hardware/markers/`), answer the
   Roomba questions on issue #1.
2. Claude: set the `pcb_*`/`usb_*` values, re-render, re-slice via
   `hardware/slicing/slice.sh`, replace the placeholder files on the printer,
   then ask Enoch to start the print.
3. After mounting: fix camera orientation flags, drop stream resolution for
   latency, reflash.

---

## 2026-09-27 - Session 1 (continued): model switch, camera power decision

**Model:** Claude Opus 5.5 (`claude-opus-5-5`) - Enoch switched models
mid-session, after everything in the Sonnet 5 entry below. First real test of
the handoff: this model picked up from the conversation plus `CLAUDE.md`,
`JOURNAL.md`, and `BOM.md`.

### Guidance from Enoch
- Offered three ways to power the T-Camera and left the pick to Claude: a
  spare 3.7V Li-ion pack on the board's own battery connector, a 5-pin
  connector on the bottom of the board that can supply power, or cutting a
  spare USB cable.

### What happened
- Picked the spliced USB cable (buck converter at 5.0V -> micro-USB input).
  Why not the others:
  - **Separate 3.7V pack:** works electrically (it's what the board's IP5306
    charger is designed for), but it's a second battery to monitor and, in
    Phase 2, a second thing to recharge. One pack keeps one charging target,
    and the battery monitoring already calibrated covers it.
  - **5-pin bottom connector:** its pinout would need verifying before
    trusting it; USB is the documented, known-safe input.
- Wiring spec written up for Enoch (and logged in `BOM.md`): buck input on the
  L298N's +12V/GND terminals, downstream of the rover's power switch so the
  camera powers off with the rover; set and verify 5.0V output with a
  multimeter before connecting; verify USB wire colors by continuity; data
  wires unconnected and insulated; camera's JST battery connector left empty.

### Decisions
**Claude-driven:** choosing the power source, and the tap point downstream of
the power switch.

**Enoch-decided:** offering the options and delegating the choice; he does the
physical splice and wiring.

### Backup battery, and handoff to the next model

Enoch offered to add his spare 3.7V Li-ion pack as a *dedicated backup* on the
T-Camera's own JST connector, alongside USB power, so the camera survives a
main-pack depletion. Decided: yes, but after the USB path is built and
verified. The IP5306 runs the board from USB and charges the cell, then fails
over to the cell if USB drops. Caveat to measure, not guess: while charging,
the IP5306 can pull up to ~2A through the buck converter, all from the main
pack, which will cut drive time until the cell is full. Logged in `BOM.md`.

Enoch is switching models again and splicing the USB cable in the morning.
**Open work for the next session, explicitly authorized by Enoch:**
1. **Camera firmware.** Update the T-Camera's firmware for its new on-rover
   role, either as an ESPHome update or a rewrite from scratch, reflashing
   the device as needed (hostname `redcam`; the current config is
   `wrovercam.yaml` in the private ESPHome repo). Per `CLAUDE.md`, anything
   written goes in this repo with scripted installs.
2. **Camera mount (design + slice).** Constraints from Enoch:
   - It attaches to the Makeblock Starter Robot Kit chassis: a horizontal
     main plate with lots of regularly spaced holes, like a small pegboard.
     Research the kit's actual parts and hole spacing/screw size rather than
     guessing.
   - Account for the camera's orientation on the board. The current config
     sets `horizontal_mirror: true`, `vertical_flip: true`, and OLED
     `rotation: 180`, which suggests the board is currently mounted upside
     down. Once it's mounted upright on the rover, those flags probably need
     flipping.
   - The board also carries a PIR motion sensor and an OLED. The mount
     shouldn't block either, and ideally keeps the OLED readable.
   - Leave room for the micro-USB power lead and, later, the backup cell.
   - Printer: Sidewinder X4 Plus S1, PETG loaded. Claude slices; Enoch starts
     the print.
3. **Waiting on Enoch:** the USB splice and wiring (spec above), then the
   cliff sensors when they arrive.

**Claude-driven:** timing the backup cell after USB verification, and flagging
the charge-current draw on the main pack.
**Enoch-decided:** offering the backup cell, authorizing firmware work and
mount design, and the mount constraints.

---

## 2026-09-27 - Session 1: First drive + safety hardening

**Model:** Claude Sonnet 5 (`claude-sonnet-5`)

### Guidance from Enoch this session
- Mission: drive the rover around the garage workbench without falling off
  the edge (the right side of the camera view was flagged as the fall risk),
  using the existing fixed workbench camera as the only eyes. Update the
  ESPHome config as needed; more hardware can be added on request; an ESP32
  alternative controller was offered if it would help (later clarified as an
  ESP32-WROVER T-Camera already on hand, not the S3 variant).
- Explicitly told to prompt for any access needed (e.g. camera credentials)
  rather than guessing or working around it.
- Hardware context provided as it became relevant: 3x 18650 Li-ion cells,
  L298N dual H-bridge driving 2 motors, an MCP23008 GPIO expander used
  specifically because the D1 Mini didn't have enough spare pins to drive the
  L298N directly, and the L298N's onboard 5V regulator (rated ~0.5A) is what
  powers the D1 Mini - fed from the raw battery rail, not a separate supply.
- Firmware/hardware direction largely left to Claude's judgment ("optimize
  the config... or write custom firmware... let me know if you want me to add
  components").
- Longer-term mission shape: solve the workbench/fall-hazard problem solidly
  first, *then* expand to roaming the whole house - a signal that navigation
  safety now should anticipate that later, higher-stakes phase.
- Wanted a public GitHub repo to track and show off progress, with a hard
  requirement to scrub all secrets/IPs/usernames/passwords/WiFi SSIDs before
  anything is published.
- Wanted a link to that repo added to the workbench project's spot on the
  Home Assistant dashboard.
- Wanted this journal: dated, model-tagged, resumable across sessions *and*
  model switches, summarizing the guidance given, and honest about
  Claude-driven vs. Enoch-decided calls.
- Wanted a maintained BOM (what's actually in the design) and a shopping list
  (what Claude needs Enoch to acquire), with a standing **$100 budget** for
  anything not already in Enoch's inventory - documented in the repo.

### What happened
- Got camera access working: the workbench ONVIF camera (Thingino firmware)
  needed Basic auth; the saved username turned out to be wrong - Thingino's
  login is always `root`, regardless of what's saved. Also found that the
  camera's `preview.cgi` returns an HTML viewer page, not an image; the real
  snapshot endpoint is `image.cgi`.
- The first snapshot was pitch black; turned on the garage workbench light
  via Home Assistant before continuing.
- Drove the rover directly over ESPHome's **native API**, bypassing Home
  Assistant entirely - its connection to this device turned out to be stale
  (entities showing unavailable despite the device being online). Confirmed
  all five existing services work: `forward`, `backward`, `left`, `right`
  (the latter two are in-place pivot turns), `stop`. Drove forward a full
  bench-length, pivoted, backed off from some bench clutter it was closing in
  on, and pivoted the other way - staying clear of the flagged edge the whole
  time.
- Identified a real safety gap: nothing stopped the motors if whatever was
  driving the rover crashed or the network dropped mid-command. Added two
  protections to the firmware:
  - **Command watchdog** - any drive command auto-stops if not refreshed
    within 1.5s.
  - **Disconnect-triggered stop** - motors stop the instant the controlling
    API client disconnects, for any reason.
  - Verified the second one for real: fired `forward`, disconnected without
    ever sending `stop`, reconnected two seconds later, and confirmed the
    rover had already stopped itself.
- Scaffolded two more safety layers into the firmware ahead of the hardware
  existing, so they activate the moment it's wired in with no further
  firmware changes:
  - **Cliff detection** - two IR reflectance sensors on the GPIO expander's
    two free pins; forward/turn commands refuse to run while either sensor
    reports no surface underneath (backward stays allowed, so it can always
    retreat from an edge).
  - **Battery cutoff** - a voltage sensor on the D1 Mini's one analog pin;
    drive commands refuse below ~9.3V pack voltage, recovering at 9.6V.
- Caught and fixed a config bug along the way: adding the new battery sensor
  block had silently replaced - rather than merged with - the device's
  existing uptime/WiFi-signal sensors, because of how this file combines
  shared config fragments. Restored them. (Noted, but left alone as
  out-of-scope: the same underlying issue already affected two *other*
  sensors from before this session.)
- Built and pushed the public repo, `github.com/moellere/rover`: a
  mission-log README, a reference copy of the firmware, and three sanitized
  scripts (a drive CLI, the disconnect-safety test, and a camera-snapshot
  helper). Everything was scanned for IPs/hostnames/paths/credentials before
  the initial push. Creating the actual GitHub repo needed Enoch to run the
  command himself - a safety guardrail blocks Claude from creating public-
  facing surfaces unilaterally.
- Added a link to the repo on the Home Assistant "Garage" dashboard section,
  next to the existing workbench-light control.

### Decisions

**Claude-driven** (identified, designed, or implemented without being asked
for that specific thing):
- Diagnosing the stale Home Assistant connection and switching to direct
  native-API control instead of troubleshooting HA further.
- Identifying the no-timeout/no-disconnect-handling safety gap and designing
  the watchdog + disconnect-stop fix.
- Designing the cliff-sensor and battery-cutoff scaffolding: pin choices,
  voltage thresholds, and which drive directions each guard blocks (backward
  deliberately stays allowed under a cliff condition).
- Catching and fixing the sensor-merge config bug.
- The repo's structure, contents, and sanitization pass.

**Enoch-decided:**
- The mission and its phases (workbench first, house-wide later).
- Battery pack configuration (3S) and the wiring/tap-point clarifications for
  the divider.
- Confirming "write the cliff-sensor config now" and "3S, ~12.6V" when asked
  directly via a scoped question.
- Repo name and visibility (`rover`, public) and what it should contain.
- Actually creating the GitHub repo (Claude was blocked from doing this
  unilaterally).
- This journal/BOM/budget system itself, including the $100 budget policy.

### Update, same session - divider wired, IR sensors ordered

Enoch confirmed the exact chassis (a Makeblock Starter Robot Kit, tank
configuration) for the BOM, wired the battery-voltage divider per the
confirmed schematic (100kΩ/27kΩ from the L298N's +12V terminal to the D1
Mini's A0), and ordered the two IR cliff sensors himself - directly, not
against Claude's $100 budget. BOM updated accordingly: the divider moves to
Installed, the cliff sensors show as Ordered. Next step on the battery side
is calibrating the `multiply` constant in `rover.yaml` against a real
multimeter reading, once convenient.

Enoch also said this session is ending here for now, with a model switch to
follow - a first real test of whether this journal actually does its job of
letting a different model pick things up cleanly.

### Update, same session - battery sensor calibrated

Before wrapping up, Enoch asked whether the voltage reading had actually been
tested - it hadn't; the sensor had only ever been read with the placeholder
`multiply: 15.0`. Read it live: 11.3232V. Enoch measured the pack directly
with a multimeter: 11.79V. Solved for the correct factor
(`11.79 / (11.3232 / 15.0) = 15.618`), updated `rover.yaml`, recompiled,
OTA-flashed, and re-read the sensor: 11.77V - within noise of the multimeter
reading. Battery monitoring is now fully installed and verified accurate, not
just wired.

### Update, same session - project constraints, next milestone, documentation policy

Enoch turns didn't actually end the session yet - three more rounds of
guidance came in before the model switch:

1. Asked what Claude would tackle next (besides the already-ordered cliff
   sensors), and laid out the standing constraints this project operates
   under: never harm a person or animal, never intentionally damage property
   or equipment, stay within budget, break no laws knowingly - and within
   those limits, expand capabilities freely for experimentation, science,
   and fun. Parts requests go through Enoch; anything he already has doesn't
   count against budget, anything he doesn't goes on the shopping list and
   draws the budget down. Claude is expected to research parts and current
   pricing before asking for a purchase. Budget increases happen at Enoch's
   discretion as milestones are hit. 3D printing is available (a Sidewinder
   X4 Plus S1, currently loaded with PETG, with a camera attached for
   monitoring) - Claude designs and slices, Enoch loads/starts the actual
   print. Physical building/soldering gets discussed before either of them
   just does it.
   - Claude's pick for "what's next": mount the already-owned, currently
     unused ESP32-WROVER T-Camera on the rover for onboard vision - zero
     budget cost, and necessary before Phase 3 (the fixed workbench camera
     won't help once the rover leaves that room). Flagged one open question
     before committing: the L298N's 5V regulator is already tight at 0.5A,
     so the camera almost certainly needs its own power path rather than
     sharing that rail - asked Enoch to identify the T-Camera board's exact
     input spec.
2. Enoch confirmed he has buck converters in inventory already, covering
   that power-path need at no budget cost if one turns out to be necessary -
   specifically LM2596 adjustable modules (4.5-40V in, 1.25-37V out, ~2-3A),
   comfortably able to run the pack straight down to whatever the T-Camera
   needs. Logged in `BOM.md`. Still waiting on the T-Camera's exact input
   spec before setting the output voltage - 5V is the likely answer but
   unconfirmed.
3. Added a documentation/software policy: keep the journal, BOM, and other
   docs current *as changes happen*, not after the fact. Prefer open-source
   software over writing new code; if something has to be written, it goes
   in this repo; any external software this project depends on gets a
   scripted install, not manual instructions. The explicit goal: someone
   else should be able to clone this repo and actually reproduce the build.

Created `CLAUDE.md` at the repo root to hold all of this as a standing
rulebook - it's auto-loaded by Claude Code as project instructions for any
future session in this repo, on any model, which directly serves the
"pick up where we left off across model switches" goal this whole
journal/BOM/CLAUDE.md system exists for. Updated `BOM.md` with an "in
progress" section tracking the camera-mount investigation (buck converter,
3D-printed mount) ahead of it becoming a full BOM line.

**Claude-driven:** picking the onboard-camera milestone and its
justification; identifying the shared-regulator power risk before it caused
a problem; the `CLAUDE.md` structure and what it captures.

**Enoch-decided:** the constraints themselves, the budget mechanics, the 3D
printing and physical-assembly workflow, confirming buck converters are on
hand, and the documentation/software policy in full.

### Update, same session - identified the camera, researched its power spec

Enoch identified the exact board: a TTGO T-Camera, ESP32-WROVER-B,
OV2640 V1.7, already on the network (hostname `redcam`) and reflashable.
Turned out this isn't the unused spare assumed earlier - it's
an *existing, working* ESPHome device (`wrovercam.yaml` in the private
config repo): camera streaming at SXGA over its own web server (ports 8080
stream / 8081 snapshot), a 0.96" OLED showing motion/time/IP, a PIR motion
sensor, and a scheduled daily reboot. Currently deployed fixed and
USB-powered elsewhere - moving it to the rover means solving power for a
battery-mounted context instead.

Researched the board before wiring anything to it (avoided a real risk:
guessing wrong here could fry the board). Finding: it has an onboard IP5306
power-management chip whose battery JST connector expects a **single-cell
3.7V LiPo** - directly wiring the rover's 3S pack (9-12.6V) there would
damage the charge IC. The board also accepts power via **micro-USB (5V)**,
a safe, standard, documented path. Plan: LM2596 buck converter set to 5.0V
(verify with a multimeter first) feeding into the T-Camera's micro-USB
input, not its battery connector. Logged in `BOM.md`, including the one
remaining open decision: splice a spare USB cable (free, destructive) vs.
buy a small USB breakout/screw-terminal adapter (~$1-2, clean) to actually
deliver that 5V into the port - left for Enoch per the "discuss before
building" rule in `CLAUDE.md`.

Also noted: the rover itself is powered off for the night (batteries saved,
not a firmware/config state).

**Claude-driven:** researching the board's real power spec before acting on
an assumption, and catching the JST/LiPo-connector risk before it became a
mistake.

**Enoch-decided:** identifying the exact board and confirming it's
reflashable; still pending his choice on cable-splice vs. breakout adapter.
