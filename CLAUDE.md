# Rover Project Instructions

The rover's name is **Grover** (named 2026-09-29: blue Makeblock rails,
and it spends its life doing "near... far"). Use it.

This file is automatically loaded by Claude Code as project instructions
whenever a session (any model) works in this repo. It's also the
plain-language rulebook for the project, for a human reader.

**Read this first, then [JOURNAL.md](JOURNAL.md) for what's actually
happened and where things currently stand, then [BOM.md](BOM.md) for parts,
then [ROADMAP.md](ROADMAP.md) for what's planned next.**
Those three files together are the whole handoff package - a new session,
on any model, should be able to read them and continue the project without
Enoch having to re-explain context.

## Mission

1. **Phase 1:** drive around the garage workbench without falling off the edge.
2. **Phase 2:** figure out recharging.
3. **Phase 3:** roam the house.

**Proposed next goal after Phase 1 (Claude's pick, 2026-09-28, Fable 5.1;
Enoch can veto or reshape it): visual homing.** From anywhere on the bench,
the rover finds a printed marker with its onboard camera and parks nose-on
within ~2 cm of it, with no human input. It's the front half of docking
(find dock -> align -> drive onto contacts), so it feeds Phase 2 directly,
and it's measurable. Prerequisites: the onboard camera mounted and powered,
cliff sensors installed.

## Architecture (decided 2026-09-28)

Three layers: an ESP32 (`rover32`, since 2026-10-03; was a D1 Mini) is the
**spinal cord** (ESPHome; watchdog, disconnect-stop, cliff, battery and
TFMini obstacle guards in firmware - authoritative), the
T-Camera is the **eyes** (ESPHome; snapshot/stream), and `brain/` is the
**brain** - an off-board MCP server where autonomy lives. Drive the rover
through the `rover-brain` MCP tools, not ad-hoc scripts. Consolidating both
ESPs onto one board is a known later step (see BOM.md), not now.

**Chassis (decided 2026-09-29):** the Makeblock kit is built as the
**trike** (two driven wheels + trailing caster), not the tank. Tank tracks
had to skid sideways to pivot, which caused stiction and left/right
asymmetry. Steering is still differential, so `left`/`right` mean the same
thing. The kit's Me Orion board is *not* used - an ESP + ESPHome stays
(Orion has no WiFi and the safety firmware is proven). The swivel caster
twists the rear on stops; a fixed printed skid replaces it (2026-10-05).

## Homing runs need a clear lane

The TFMini guard stops for things **straight ahead** above ~5 cm, but its
2.3 deg beam misses anything off-centre or low (cables, mats, a box corner,
a table leg seen at an angle). Check the lane on a bench camera before a
run, keep the marker's approach clear, and when driving anywhere else take
a camera frame after every pulse (house run, 2026-10-04).

## Reversing the trike

Backing up is **not** the mirror of driving forward: the trailing caster has
to flip 180° when direction changes and drags the rear sideways while it
does (2026-09-29: three 0.3 s backward pulses turned the rover ~45° and put
one wheel over the right-hand bench edge; Enoch caught it). No rear cliff
sensors exist, and the rover camera faces *away* from the direction of
travel - marker distance says nothing about sideways drift. Reverse only in
single short pulses (<= 0.3 s), and **look at the bench camera before each
one** - never a scripted sequence checked only through the rover camera.

## Rover orientation on the bench

Since 2026-10-05 the `bench` camera is **fishcam, mounted overhead looking
straight down** (PTZ; pan sweeps along the bench). In its frame the marker
end is on the **left**, the open garage-side edge along the **top**, the
pegboard along the **bottom**. Grover's heading reads directly off its
outline - check it, and the lane, before every run and before any reverse.
`camv3` (until now the rear view) is moving to the Eufy's lid; the brain's
`front` name points at it until it's renamed `eufy`.

**The bench has a hatch** (the outlined rectangular panel in the middle of
the overhead frame) whose edge has a slight lip. A wheel catching it yaws
Grover 20-30 deg (seen from overhead 2026-10-05). Plan runs around it, or
cross it square and slowly. The black T-shaped object beside it is Enoch's
solder fume fan - an obstacle, not part of the bench.

(History: camv3 used to watch Grover's rear at bench level, and Claude got
`forward`/`backward` backwards once from that view, 2026-09-28. With the
overhead view, read the direction from the frame each time.)

## Token budget

Enoch's Claude usage has a limit per model. Work in bounded chunks, don't
poll or loop while waiting on him, and don't burn tokens on speculative
work he hasn't asked for. If the current model's limit runs out, the
fallback is to switch to Opus 5.5 or wait for the reset.

## Constraints (hard rules)

- Never cause harm to any individual or animal.
- Never intentionally damage property or equipment.
- Stay within budget (see Budget below).
- Break no laws, knowingly.
- Within those limits: expand capabilities freely, in the name of
  experimentation, science, and fun.

## Budget & parts

- Standing budget: **$100**, tracked in [BOM.md](BOM.md).
- If Enoch already has a part in inventory, he supplies it and it does not
  count against the budget.
- If he doesn't have it, it goes on the shopping list in `BOM.md` and draws
  down the budget once actually purchased.
- Research parts and current pricing before asking Enoch to buy anything -
  don't guess at prices, and don't ask him to buy something without knowing
  what it costs.
- As milestones are hit, Enoch may add to the budget - that's his call, not
  something to assume or ask for preemptively.

## Standing permissions

- **Dedicated to this project, flash/modify freely** (Enoch, 2026-09-29,
  "for the time being"): the rover's spinal cord (`rover32`), the
  T-Camera (`redcam`), both bench cameras (`camv3`, `fishcam`), the
  Eufy's lid board (`blackcam`) and the IR test nodes (`eufy-ir8266`,
  `eufy-ir-c3`). Every other device still needs a check-in first.
- **Physical setup is Enoch's to confirm.** When a test needs him to move,
  aim or wire something, describe the setup and wait for his "go" before
  capturing or sending - don't start while he's still placing things.

## Choosing the next step (Enoch, 2026-09-29)

Claude picks what to work on next and moves through milestones without
asking permission ("you tell me what you want to do next"). Say what's
next and why, then do it. Physical work (soldering, assembly) is still
discussed with Enoch first, and purchases still follow the budget rules.

## Resources on the table (Enoch, 2026-09-29)

This is Claude's project to drive toward the goals; use whatever it needs:

- **Brain hosting.** The brain runs as a script on the dev VM today, which
  is fine for bench work but the VM may be resource-constrained and a
  script isn't robust for unattended operation. For Phase 3, package
  `brain/` as a container with its MCP endpoint hosted like the other
  homelab MCP servers; ask the homelab-helper MCP (`recommend_placement`)
  or that session where it should run.
- **Firmware.** ESPHome is a choice, not a constraint - custom firmware on
  the rover's board is fine if it is **OTA-flashable**. Current position:
  keep ESPHome for the reflex layer (fast iteration, clear safety logic);
  go custom (ESP-IDF + OTA) only when perception has to run on the bot.

## Hardware workflow

- New components can be designed/specified and requested from Enoch freely
  within the constraints above.
- 3D printing: a Sidewinder X4 Plus S1 is available, currently loaded with
  PETG, with a camera attached for monitoring prints. Claude designs and
  slices the part; Enoch loads filament changes and actually starts the
  print job. Slicing preferences (Enoch's): **tree supports** when supports
  are needed at all, and **no brim** (he doesn't want to trim one off).
  Designs are parametric OpenSCAD in `hardware/`; the toolchain installs
  with `scripts/install-tools.sh` (OpenSCAD + OrcaSlicer, no root needed).
  Prints are submitted and started through the print-warden MCP (since
  2026-09-29), never through the printer's API directly; starting needs
  Enoch's OK, quoted, and he cancels. `scripts/warden_call.py` is the
  fallback when the MCP isn't loaded in the session.
- **Eufy IR hold (2026-10-09): send no Eufy commands** until the frame's
  hour encoding is verified against the real remote. Our 12-h stamps
  probably shifted the vacuum's clock, turning a cleaning schedule into a
  daily 6 PM run that twice drove it out an open garage door.
- **The Eufy is tested on the floor, never on the workbench.** It has no rear
  cliff sensors and none of the rover's firmware guards; on 2026-09-28 it
  started reversing toward the bench edge during IR testing and Enoch caught
  it. Never leave the IR node aimed at it unattended.
- Cameras at night: turn the garage workbench light on just before taking a
  picture (bench cam or printer cam), then back off. Don't leave it on.
- Soldering, assembly, or other physical building: discuss with Enoch first
  rather than assuming an approach - he does or supervises the physical
  work.

## Software policy

- Prefer existing open-source software over writing something new.
- If nothing suitable exists, write it - and it goes in this repo.
- Any external software this project depends on gets an install script
  committed here, not just documented manual steps.
- Goal: someone else should be able to clone this repo and actually
  reproduce the build, not just read about it.

## Documentation policy

- Keep `JOURNAL.md` and `BOM.md` current **as you go**, not as an
  afterthought - every session that changes something updates both before
  it ends.
- **Commit and push regularly** (Enoch, 2026-09-28): after each coherent
  change, not in one batch at the end of a session. **Documentation updates
  in this repo never need Enoch's permission** (2026-09-29) - keep README,
  JOURNAL, BOM, ROADMAP and the hardware/brain READMEs current and push.
  README is the "what it is now" snapshot, JOURNAL the history, BOM and
  ROADMAP the ledgers: rewrite in place, don't accumulate. Work on `master`; if a
  branch is ever used, merge it back the same session so the remote is
  never behind the working tree for long. Run the secrets/IP scan before
  every commit.
- `JOURNAL.md` entries are tagged with the model that did the work, a
  summary of the guidance given that session, what happened, and a
  Claude-driven vs. Enoch-decided breakdown of notable calls - see that
  file's own header for why.
- Secrets, IPs, hostnames, and credentials never go in this repo - it's
  public. The canonical, secret-containing ESPHome config lives in a
  private homelab repo; only a sanitized reference copy lives here
  (`firmware/rover.yaml`).
