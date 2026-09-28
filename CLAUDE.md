# Rover Project Instructions

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

Three layers: the D1 Mini is the **spinal cord** (ESPHome; watchdog,
disconnect-stop, cliff and battery guards in firmware - authoritative), the
T-Camera is the **eyes** (ESPHome; snapshot/stream), and `brain/` is the
**brain** - an off-board MCP server where autonomy lives. Drive the rover
through the `rover-brain` MCP tools, not ad-hoc scripts. Consolidating both
ESPs onto one board is a known later step (see BOM.md), not now.

## Rover orientation on the bench

The bench camera looks at the rover's **rear** (the 18650 pack faces the
camera). So `forward` drives *away* from the camera toward the pegboard and
the marker; `backward` drives *toward* the camera and the near edge. Claude
got this backwards once (2026-09-28); check the frame before choosing a
direction.

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

- **The T-Camera (`redcam`) may be reflashed without asking** - firmware
  updates, rewrites, config changes, all of it. Granted by Enoch 2026-09-28,
  scoped to that one device.
- **The IR bridge (`eufy-ir`) may also be reflashed** - Enoch OK'd it
  2026-09-28 when the captured codes went in. Every other device still
  needs a check-in first (the rover itself included).

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
  change, not in one batch at the end of a session. Work on `master`; if a
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
