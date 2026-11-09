"""Exploded drawing of the nose bumper: back plate, lever microswitches, floating bar,
screws (2026-11-09).

    uv run --with numpy-stl --with matplotlib python scripts/nose_bumper_exploded.py OUT.png
"""
import subprocess, sys, tempfile, numpy as np
sys.path.insert(0, "scripts")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from stl import mesh
from nose_assembly_views import draw, SCAD, OPENSCAD
items = [("b_body", (0.25, 0.45, 0.85), "nose module: fixed back plate + switch platform at each end"),
         ("b_ms", (0.12, 0.12, 0.12), "lever microswitch x2, lever edge FORWARD, lever tip touching the bar"),
         ("b_bar", (0.55, 0.75, 1.0), "bumper bar (separate print)"),
         ("b_screws", (0.85, 0.1, 0.1), "M3 x 16 x2 from BEHIND the plate into the bar; M2 x 10 x2 per switch, down into the platform")]
def iso(az, el):
    az, el = np.radians(az), np.radians(el)
    d = np.array([np.sin(az) * np.cos(el), np.cos(az) * np.cos(el), np.sin(el)])
    sx = np.cross([0, 0, 1], d); sx /= np.linalg.norm(sx); return np.array([sx, np.cross(d, sx), d])
fig, ax = plt.subplots(2, 1, figsize=(18, 15))
for a, ex, R, title in ((ax[0], 30, iso(25, 30), "EXPLODED - from ahead-right, above: the bar slides straight back onto the guide screws"),
                        (ax[1], 0, iso(65, 25), "ASSEMBLED - from the right, above (bar 5.5 mm ahead of the plate, levers just touching it)")):
    ms = []
    with tempfile.TemporaryDirectory() as t:
        for p, c, l in items:
            f = f"{t}/{p}.stl"
            subprocess.run([OPENSCAD, "-D", f'part="{p}"', "-D", f"explode={ex}", "-o", f, SCAD], check=True, capture_output=True)
            ms.append((mesh.Mesh.from_file(f), np.array(c), l))
    draw(a, ms, R, title); a.axis("off")
fig.legend(handles=[Patch(color=c, label=l) for _, c, l in items], loc="lower center", ncol=2, fontsize=12)
fig.text(0.02, 0.5, "Fit order:\n1. Switches on their platforms, lever edge\n   forward, M2 x 10 x2 each (pilots in the\n   platform); solder leads first.\n2. M3 x 16 through the plate from BEHIND\n   (heads behind the plate).\n3. Hold the bar in front, its bosses on the\n   screw tips; drive the screws in until the\n   bar sits 5.5 mm ahead of the plate with the\n   levers just touching it. Don't overtighten:\n   the screw heads are the forward stop and the\n   bar must slide back freely ~2 mm.\n4. Press each end: click, and the stop bosses\n   meet the plate before the switch bottoms.", fontsize=12, va="center", family="monospace")
plt.tight_layout(rect=(0.2, 0.05, 1, 1)); plt.savefig(sys.argv[1], dpi=70)
