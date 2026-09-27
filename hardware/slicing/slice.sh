#!/usr/bin/env bash
# Slice an STL for the Sidewinder X4 Plus in PETG with the house rules
# (no brim, tree supports on auto). Produces <name>.3mf and <name>.gcode.
#   usage: hardware/slicing/slice.sh path/to/part.stl [outdir]
set -euo pipefail
STL="$1"; OUT="${2:-$(dirname "$STL")}"; NAME="$(basename "${STL%.stl}")"
HERE="$(cd "$(dirname "$0")" && pwd)"
P="$HOME/.local/opt/orcaslicer/squashfs-root/resources/profiles/Artillery"
FLAT="$HERE/../../scripts/orca_flatten_preset.py"
TMP="$(mktemp -d)"
python3 "$FLAT" "$P" machine  "Artillery Sidewinder X4 Plus 0.4 nozzle"       "$TMP/machine.json"
python3 "$FLAT" "$P" process  "0.20mm Standard @Artillery X4Plus 0.4 nozzle" "$TMP/process.json" "$HERE/house-rules.json"
python3 "$FLAT" "$P" filament "Artillery Generic PETG"                        "$TMP/filament.json"
xvfb-run -a "$HOME/.local/bin/orca-slicer" \
  --load-settings "$TMP/machine.json;$TMP/process.json" --load-filaments "$TMP/filament.json" \
  --slice 0 --export-3mf "$NAME.3mf" --outputdir "$OUT" "$STL" >"$TMP/orca.log" 2>&1 || { tail -20 "$TMP/orca.log"; exit 1; }
python3 - "$OUT/$NAME.3mf" "$OUT/$NAME.gcode" <<'PY'
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1]); g = [n for n in z.namelist() if n.lower().endswith(".gcode")]
if not g: raise SystemExit("no gcode inside 3mf - slicing failed")
data = z.read(g[0]).decode(errors="ignore"); open(sys.argv[2], "w").write(data)
for l in data.splitlines():
    if l.startswith(";") and any(k in l.lower() for k in ("estimated printing time", "total filament used", "filament used [g]")):
        print(l.strip("; "))
PY
echo "wrote $OUT/$NAME.3mf and $OUT/$NAME.gcode"
rm -rf "$TMP"
