# Hardware designs

Parametric OpenSCAD parts for the rover. Install the toolchain with
`scripts/install-tools.sh` (OpenSCAD 2021.01 + OrcaSlicer 2.4.2, no root
except for the one `apt-get` line noted at the top of that script).

## Parts

| File | What | Status |
|---|---|---|
| `camera-mount.scad` | Cradle that stands the TTGO T-Camera upright on the Makeblock plate, lens/PIR/OLED facing forward, tilted 10° down. Open front, back window for the micro-USB lead, M4 slots on the plate's 8mm grid. | Designed and renders clean. **Board dimensions are placeholders** - measure the real board and set the `pcb_*` values before printing. |

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
