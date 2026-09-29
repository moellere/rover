> Note (rover session): this repo is public; LAN addresses were removed from this note on
> arrival. Hosts live in `~/.rover-brain.env` and the user-scope `claude mcp` entries.

# Handoff: bench camera swap (from the homelab-helper / print-warden session, 09/29/2026)

**Proposal, agreed with Enoch on 09/28/2026:** the rover's bench camera changes from **camv3** to
**fishcam**. camv3 moves to the Sidewinder X4 as the fixed whole-bed camera for print-failure detection.
Nothing has been moved yet; Enoch will do the physical swap when he gets to it. This note is so the rover
side is ready and nothing silently breaks.

## What changes for the rover

| | Today | After the swap |
|---|---|---|
| Bench camera | camv3, Wyze Cam v3 on Thingino, (camv3's LAN address - see ~/.rover-brain.env), fixed | fishcam, Wyze Cam **Pan** v2 on Thingino, (fishcam's LAN address - kept out of this public repo), **PTZ** |
| `BENCH_CAM_HOST` in `brain/` | (camv3's LAN address - see ~/.rover-brain.env) | (fishcam's LAN address - kept out of this public repo) |
| Snapshot path | `/x/image.cgi` (basic auth) | same firmware, same path expected; confirm the password (Thingino creds are per camera) |
| PTZ | none | yes, already exposed in Home Assistant via the ONVIF integration (`camera.wyzecampanv2_1_profile_1`, `onvif.ptz` service). Two presets suggested: "bench" for the marker/rover view, "wide" for the whole table |
| Frigate | both cameras stay in Frigate on covomv under their current names; snapshots also available at `the Frigate server's `/api/<name>/latest.jpg`` | unchanged |

Things to watch after the move:
- `find_marker` was calibrated against camv3's mount and lens. fishcam has a different sensor, lens and
  height, so expect a one-time re-check of marker size/bearing and the "bench" preset aim.
- camv3 has been flapping on 2.4 GHz through the playroom AP (182 ffmpeg restarts in 48 h on 09/28). fishcam
  is coming from the dining room; after the move, check it associates with the **garage** AP (the X4 does)
  and pin it in UniFi if it clings to another one.
- The overlay text (timestamp/name) on the Thingino stream is fine for the rover; it will be turned off on
  camv3 only, for the print detector.

## Context you may want

- Print side: the C920 on the X4's X beam stays as the nozzle/layer camera; camv3 becomes the elevated
  fixed view (200 mm above the bed, 35° down, on a post from the left base rail or off-machine).
  Drawing: https://claude.ai/artifact/7QAXDaFi9hM1tywUgeNPcZ
- Printing from the rover project now goes through the **print-warden** MCP (`print-warden` in user-scope
  `claude mcp`, the print-warden server's `/mcp` endpoint): `curl -F file=@part.stl the print-warden server's `/upload` endpoint`, then
  `submit_job(printer="covington", model="part.stl", material="PETG")` slices with your house rules (tree
  supports, no brim, Artillery X4 Plus presets) and stages the gcode; Enoch starts it from a phone tap or
  by giving permission in chat (`start_print(job_id, authorized_by=...)`). `hardware/slicing/slice.sh` still
  works locally; the warden reuses `scripts/orca_flatten_preset.py` and `house-rules.json` verbatim.
- Generic PETG white is loaded on the X4 (Spoolman spool 2); the X1 at Wyola has PETG black (spool 4).

Questions or objections: reply to the homelab-helper session (`homelab-helper-b2`) or leave a note here.
