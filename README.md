# Rover

A small tracked rover, built from Makeblock parts, living on a garage workbench.
This repo tracks its progress: mission log, control scripts, and a reference
copy of its ESPHome firmware.

## The mission

1. **Phase 1 (current):** drive around the workbench without falling off the edge.
2. **Phase 2:** figure out recharging.
3. **Phase 3:** graduate to roaming the house.

## Hardware

- Chassis: Makeblock tank tracks, two DC gear motors
- Controller: Wemos D1 Mini (ESP8266)
- Motor driver: L298N dual H-bridge
- GPIO expansion: MCP23008 I2C I/O expander (the D1 Mini didn't have enough
  spare pins to drive the L298N's 4 direction lines directly)
- Power: 3x 18650 Li-ion cells, wired 3S (~12.6V full, ~9.0V empty). The
  L298N's onboard regulator steps this down to 5V for the D1 Mini (rated
  ~0.5A - a real constraint on how much else can share that rail).
- Vision: a fixed ONVIF camera overlooking the workbench (not mounted on the
  rover itself) provides the eyes for teleop.

## Software

Firmware is [ESPHome](https://esphome.io/) (see `firmware/rover.yaml` - a
reference copy; the live/canonical version is tracked in a private homelab
config repo alongside this device's WiFi/API secrets, so this copy won't
compile standalone).

Driving happens over ESPHome's **native API** directly (bypassing Home
Assistant, whose connection to this device turned out to be stale) using
five custom services: `forward`, `backward`, `left`, `right`, `stop`. Left/right
are in-place pivot turns (one track forward, one reverse).

### Safety design

A device that can drive off the edge of a table needs more than "send stop
when you mean it." Two independent protections are always active:

- **Command watchdog** - every drive command stamps a timestamp; if 1.5s
  passes without a refresh, the firmware stops the motors on its own.
- **Disconnect safety** - if the controlling API client disconnects for any
  reason (crash, WiFi drop, script exit), the motors stop immediately.

Verified for real: `scripts/test_disconnect_safety.py` fires `forward` and
disconnects *without* sending `stop`, then reconnects a couple seconds later
and confirms the device already stopped itself.

Two more layers are wired into the firmware but waiting on hardware:

- **Cliff detection** - two downward-facing IR reflectance sensors (front
  corners) will refuse forward/turn commands the instant either one stops
  seeing the workbench surface underneath (backward stays allowed, so it can
  always retreat from an edge).
- **Battery cutoff** - a voltage divider into the D1 Mini's one analog input
  will refuse to drive below ~9.3V pack voltage (with hysteresis at 9.6V to
  resume), protecting the Li-ion cells from over-discharge.

Both are scaffolded in `rover.yaml` now (globals, sensors, guard conditions
on every drive action) so they activate the moment the sensors are wired in
- no firmware changes needed at that point.

## Scripts

- `scripts/rover_ctl.py` - CLI for driving the rover directly over ESPHome's
  native API (`list`, `forward`, `backward`, `left`, `right`, `stop`, each
  optionally with a duration for a timed pulse).
- `scripts/test_disconnect_safety.py` - the disconnect-safety regression test
  described above.
- `scripts/camera_snapshot.py` - grabs a still frame from the workbench
  camera. Documents a couple of Thingino-firmware gotchas that cost real
  debugging time (see the docstring).

All three read connection details from environment variables rather than
hardcoding them - see each script's docstring.

## Mission log

**2026-09-27 - First drive.** Got camera access sorted out (wrong username
saved initially; Thingino's default login is always `root`), turned on the
workbench light so the first snapshot wasn't pitch black, and drove the
rover forward, pivoted it right, backed it off from some bench clutter it
was closing in on, and pivoted left - confirming full directional control
while it stayed well clear of the workbench edge the whole time.

Then hardened the firmware: added the command watchdog and disconnect-safety
(and verified the latter by deliberately crashing the test script mid-command
- motors stopped on their own). Scaffolded cliff-sensor and battery-voltage
monitoring into the firmware ahead of the actual hardware going in.

![First look at the workbench, lights on](images/01-first-look.jpg)
![Mid-drive, having moved a full bench-length](images/02-first-drive.jpg)
![Parked safely after the session](images/03-parked-safe.jpg)

## Roadmap

- [ ] Wire the battery voltage divider (L298N +12V terminal -> 100k/27k
      divider -> D1 Mini A0), calibrate the scale factor against a multimeter
- [ ] Wire the two IR cliff sensors to the MCP23008's spare pins, verify
      output polarity
- [ ] Watch for brownouts once the cliff sensors share the L298N's 5V
      regulator with the D1 Mini and WiFi radio
- [ ] Figure out a charging/docking approach
- [ ] Expand the playground beyond the workbench

---

Built and driven in collaboration with Claude (Anthropic).
