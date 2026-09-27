# Sliced prints

Output of `hardware/slicing/slice.sh` (Sidewinder X4 Plus, 0.20mm, PETG, no
brim, tree supports on auto). The `.3mf` opens in OrcaSlicer for inspection;
the `.gcode` is what goes to the printer.

| File | Source | Est. time / filament | Notes |
|---|---|---|---|
| `camera-mount_v2.*` | `hardware/camera-mount.scad` with measured board dims (28.0 x 68.0 x 1.27 mm, 6 mm rear components) | see G-code header | First real print candidate. |
| `roomba-minidin-plug_v1_TESTFIT.*` | `hardware/roomba-minidin-plug.scad` | see G-code header | **Test-fit print** for the Roomba port plug - check insert fit, key, and wire holes, then tune the parameters and re-slice. |
