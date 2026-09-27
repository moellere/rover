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

Rover drives reliably via ESPHome's native API (`forward`/`backward`/`left`/
`right`/`stop`). Firmware has a command watchdog and disconnect-triggered
stop, both tested. Battery monitoring is fully installed and calibrated
(100kΩ/27kΩ divider, L298N +12V terminal -> D1 Mini A0; sensor reads 11.77V
against a multimeter's 11.79V). The two IR cliff sensors are ordered but not
yet installed; the guard logic for both is already live in firmware and will
activate automatically once wired (see [BOM.md](BOM.md) for exact status).
Home Assistant's connection to the device is stale and unused for control
(see the 2026-09-27 entry) - a future cleanup item, not a blocker. Next
milestone (see below): mount the existing TTGO T-Camera (hostname `redcam`)
on the rover for onboard vision. It already runs a working
ESPHome camera build (rebuilt and reflashed on ESPHome 2026.8.1 - pipeline
proven, snapshots work), and Claude may reflash it freely. Power path decided
(buck converter at 5.0V -> spliced USB cable -> its micro-USB input); Enoch is
building the splice. The camera mount is designed (`hardware/camera-mount.scad`)
and renders, but **needs six caliper measurements of the board** before
slicing. Slicing itself is blocked on a one-line sudo apt install on the dev
VM (Enoch offered; see the 2026-09-28 entry). The rover is powered off
overnight. Proposed next goal after Phase 1: visual homing (in `CLAUDE.md`).
Standing project rules live in [CLAUDE.md](CLAUDE.md) - read that first.

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
- Disk: the VM was at 76%. Survey done; the redundant AppImage originals
  (~180 MB, Claude's own) were removed. Enoch approved purging the
  zero-risk set (uv/esphome/pip/npm/claude-scratch caches, old ESPHome build
  dirs except the rover's): **15 GB -> 25 GB free (59% used)**. Still his
  call: an unused 2 GB Docker image, a 707 MB project cache, and the
  sudo-only housekeeping (snap revisions, apt cache, journal). A reboot is
  pending for the newer installed kernel.
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

### Open for next session
1. Enoch: measure the board (six numbers in the `.scad` header), build the
   USB splice, decide on the disk-cleanup list.
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
