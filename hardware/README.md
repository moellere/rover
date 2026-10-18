# Hardware designs

Parametric OpenSCAD parts for the rover. Install the toolchain with
`scripts/install-tools.sh` (OpenSCAD 2021.01 + OrcaSlicer 2.4.2, no root
except for the one `apt-get` line noted at the top of that script).

## Parts

| File | What | Status |
|---|---|---|
| `roomba-minidin-plug.scad` | 7-pin mini-DIN plug body for the Roomba's Open Interface port: seven solid-core wires held at the pin positions, keyed insert, gripped body. | **Shelved** - the Roomba was gone (issue #1). Test print #1 taught two fixes, now in the file: inset key groove instead of a rib, larger wire holes. Ready if a mini-DIN port reappears. |
| `camera-mount.scad` | Cradle that stands the TTGO T-Camera upright on the Makeblock plate, lens/PIR/OLED facing forward, tilted 10° down. Open front, back window for the micro-USB lead, M4 slots on the plate's 8mm grid. | Board dimensions measured by Enoch (28.0 x 68.0 x 1.27 mm, 6 mm rear components). **v5 printed and in use** (`prints/camera-mount_v5`): corner lips, straight-down cable slot, inside tabs. Known quirk: the base's cable slot breaks into its two M4 slots - use washers under the screw heads. **Tore at exactly that spot in the 2026-10-18 fall**; v6 gets a solid base, probably as a perch on the battery cradle. |
| `camera-strip.scad` | Adapter strip that bolts the v5 cradle rigidly to the chassis: spans the two front M4 standoffs (64 mm c-c, 30 mm tall, slotted for 63-66), presents the cradle's own 8 mm-grid M4 slots on top, 8 mm cable slot underneath. Runs left-right; camera centred. | Designed from Enoch's measurements 2026-09-29 (68.5 mm across the outer edges of the standoff holes). Sliced as `prints/camera-strip_v1` (21 min, 8.8 g PETG, no supports). **Printed 2026-09-29** (Enoch's go-ahead in chat). Fit-check after the trike rebuild. |
| `tfmini-bracket.scad` | TFMini bracket: sits on the front cross beam's top face, bolts through the holes at x = +/-12 mm (M4 x 20 + nut, slotted +/-2 mm front-back), with a relief pocket over the centre pair (taken by the under-beam bracket to the caster beam); a plate in front of the beam carries the sensor by its ears (M2, 36 mm c-c, Benewake drawing), centred at beam mid-height, lenses forward. Prints on the sensor face. | Beam assumed Makeblock 0824 (24 deep, 8 tall, holes mid-face on the 8 mm grid) - Enoch confirmed top/bottom holes, standard spacing, not threaded. Print-warden job `010780c633` (29 min, 7.9 g PETG), **Printed 2026-09-29** (Enoch: "OK, print it"; done in 36 min). Fit-check pending. |
| `cliff-mount.scad` | Cliff sensor mount, one per side (`side="right"|"left"` mirrors): foot on the front beam's top face at the end holes (front row, M4 x2 + nuts), plate dropping in front of the beam face past the motors, shelf at the bottom with the HW-870 module hanging under it on a 6 mm spacer boss (M3 + nut), sensor face ~8 mm above the bench, ribs stop it rotating. Prints on its side. | Beam top 51 mm above the bench, module 31.5 x 14, hole centre 7.5 mm from the pin end (Enoch, 2026-10-03). v1 right printed 2026-10-03 (Enoch: ribs stopped short of the screw, board could pivot). v2 (ribs longer along the shelf) printed left - but the ribs were only boss-high, so they never reached the board's edges. **v3** ribs come down past the board (boss + PCB + 2 mm) either side of it: staged right `3ec7dae6cc`, left `2f3cdb2627` (30 min, 9.3 g PETG each). |
| `rear-leg.scad` | Replaces the Makeblock L-bracket (sheared 2026-10-18) and the separate skid: one PETG piece, a plate on the beam stub's two M4 socket caps, a wedge web, the domed skid grown out of the foot. Prints plate-face down. | **Shelved unprinted, 2026-10-18** - the chassis goes back to the tank, which has no rear support. Kept in case the trike returns. |
| `battery-cradle.scad` | **v2 (posts):** cradle for the 3x18650 holder with the HW-288 BMS on its back (61 x 79 x ~23). Sits on the four 30 mm standoff posts over the controller (96 x 64 centres on the 8 mm grid, +/-2 mm slots, counterbored from the top), cells up, BMS flush in a floor window, zip-tie slots in the long walls, pack-lead notch in the rear wall, camera perch tab out front with a 5x2 M4 grid. Prints floor down, no supports. | Enoch's post measurements 2026-10-18 (102 x 71 outer, 30 tall). Sliced `prints/battery-cradle` (1h 52m, 42.6 g PETG); first warden job `cd828fc14e` skipped (window was centred); v2b (BMS window at the rear end, `bms_gap` 3 assumed) sliced and **awaiting Enoch's design check before staging**. body_h / bms_h still assumed (17 / 6). |
| `caster-skid.scad` | Fixed domed PETG skid replacing the swivel caster (which twisted the rear on stops). 22 mm puck, 36 mm tall (bracket underside to bench), M5 bolt down through the block into a captive nut slid in from the side. Round, so the single bolt can't steer it. | Printed and fitted 2026-10-18; its aluminium bracket sheared in the fall the same day and the skid was lost. Superseded by the tank rebuild. |

## Render

```
openscad -o camera-mount.stl camera-mount.scad
```

The `.stl` is committed alongside the `.scad` so it can be inspected without
the toolchain, but the `.scad` is the source of truth - regenerate the STL
after any edit.

## Slice and print

Printer: Artillery Sidewinder X4 Plus (Klipper/Moonraker), 300 x 300 bed,
0.4 mm nozzle, PETG loaded. OrcaSlicer ships a matching profile
("Artillery Sidewinder X4 Plus 0.4 nozzle") and a Generic PETG filament.

House rules for every slice: **tree supports** if supports are needed at
all, **no brim**. Claude slices; Enoch starts the print.

Headless slicing (no display) goes through `orca-slice-headless`, a wrapper
that runs Orca's CLI under `xvfb-run` - installed by `install-tools.sh`.
