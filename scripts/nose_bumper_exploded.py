"""Exploded drawing of the nose bumper: back plate, lever microswitches, floating bar,
screws (2026-11-09; bar v2 with leaves 2026-11-16).

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
         ("b_ms", (0.12, 0.12, 0.12), "lever microswitch x2, lever edge FORWARD, lever tip touching the bar's leaf"),
         ("b_bar", (0.55, 0.75, 1.0), "bumper bar v2 (separate print): a thin leaf behind a slot at each end presses the lever"),
         ("b_screws", (0.85, 0.1, 0.1), "M3 x 16 x2 from BEHIND the plate into the bar; M2 x 10 x2 per switch, down into the platform")]
def iso(az, el):
    az, el = np.radians(az), np.radians(el)
    d = np.array([np.sin(az) * np.cos(el), np.cos(az) * np.cos(el), np.sin(el)])
    sx = np.cross([0, 0, 1], d); sx /= np.linalg.norm(sx); return np.array([sx, np.cross(d, sx), d])
fig, ax = plt.subplots(3, 1, figsize=(18, 22))
for a, ex, R, title in ((ax[0], 30, iso(25, 30), "EXPLODED - from ahead-right, above: the bar slides straight back onto the guide screws"),
                        (ax[1], 0, iso(65, 25), "ASSEMBLED - from the right, above (bar 5.5 mm ahead of the plate, levers just touching the leaves)"),
                        (ax[2], 0, iso(0.01, 89.9), "ASSEMBLED - from straight above, FRONT at the bottom: slot and leaf at each end, stop ribs and guide pads behind the bar")):
    ms = []
    with tempfile.TemporaryDirectory() as t:
        for p, c, l in items:
            f = f"{t}/{p}.stl"
            subprocess.run([OPENSCAD, "-D", f'part="{p}"', "-D", f"explode={ex}", "-o", f, SCAD], check=True, capture_output=True)
            ms.append((mesh.Mesh.from_file(f), np.array(c), l))
    draw(a, ms, R, title); a.axis("off")
fig.legend(handles=[Patch(color=c, label=l) for _, c, l in items], loc="lower center", ncol=2, fontsize=12)
fig.text(0.02, 0.5, "Fit order:\n1. Switches on their platforms, lever edge\n   forward (already fitted).\n2. M3 x 16 through the plate from BEHIND\n   (heads behind the plate).\n3. Hold the bar in front, its guide pads on\n   the screw tips; drive the screws in until\n   the bar sits 5.5 mm ahead of the plate with\n   the levers just touching the leaves.\n   Don't overtighten: the screw heads are the\n   forward stop and the bar must slide back\n   freely 3.5 mm.\n4. Press each end: click early in the travel;\n   the stop ribs meet the plate at 3.5 mm.\n   If a lever bottoms first, its leaf gives\n   (up to 1.2 mm).", fontsize=12, va="center", family="monospace")
plt.tight_layout(rect=(0.2, 0.05, 1, 1)); plt.savefig(sys.argv[1], dpi=70)
