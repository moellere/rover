# Sliced prints

Output of `hardware/slicing/slice.sh` (Sidewinder X4 Plus, 0.20mm, PETG, no
brim, tree supports on auto). The `.3mf` opens in OrcaSlicer for inspection;
the `.gcode` is what goes to the printer.

| File | Source | Est. time / filament | Notes |
|---|---|---|---|
| `camera-mount_v1_PLACEHOLDER-DIMS.*` | `hardware/camera-mount.scad` @ commit noted in git log | 1h 14m, 17.2 g | **Placeholder board dimensions** - a pipeline check, not for printing. Re-slice after the `pcb_*`/`usb_*` values are measured. |
| `roomba-minidin-plug_v1_TESTFIT.*` | `hardware/roomba-minidin-plug.scad` | see G-code header | **Test-fit print** for the Roomba port plug - check insert fit, key, and wire holes, then tune the parameters and re-slice. |
