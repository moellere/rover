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
stop, both tested. Cliff-sensor and battery-cutoff logic is written into the
firmware but inert - waiting on the physical sensors/divider (see
[BOM.md](BOM.md)). Home Assistant's connection to the device is stale and
unused for control (see the 2026-09-27 entry) - a future cleanup item, not a
blocker.

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
