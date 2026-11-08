"""Exploded drawing of the right cliff mount (wing, board, shoe, screws), 2026-11-08.

    uv run --with numpy-stl --with matplotlib python scripts/nose_cliff_exploded.py OUT.png
"""
import os, subprocess, sys, tempfile, numpy as np
sys.path.insert(0, "scripts")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from stl import mesh
from nose_assembly_views import draw, SCAD, OPENSCAD
items = [("x_body", (0.25, 0.45, 0.85), "nose module (wing: shelf, boss, end wall)"),
         ("x_board", (0.1, 0.6, 0.25), "HW-870 board + TCRT5000"),
         ("x_shoe", (0.95, 0.55, 0.1), "shoe (new separate print): socket + skids"),
         ("x_screws", (0.8, 0.1, 0.1), "screw paths: M3 x 14 (inboard, nut on the shelf), M2 x 10 (up into the end wall)")]
fig, ax = plt.subplots(1, 2, figsize=(20, 9))
for a, ex, title in ((ax[0], 22, "EXPLODED - right side, from ahead-right and below: fit order bottom -> top"), (ax[1], 0, "ASSEMBLED")):
    ms = []
    with tempfile.TemporaryDirectory() as t:
        for p, c, l in items:
            f = f"{t}/{p}.stl"
            subprocess.run([OPENSCAD, "-D", f'part="{p}"', "-D", f"explode={ex}", "-o", f, SCAD], check=True, capture_output=True)
            ms.append((mesh.Mesh.from_file(f), np.array(c), l))
    az, el = np.radians(35), np.radians(-20)   # from ahead-right, slightly BELOW
    d = np.array([np.sin(az) * np.cos(el), np.cos(az) * np.cos(el), np.sin(el)])
    sx = np.cross([0, 0, 1], d); sx /= np.linalg.norm(sx); sy = np.cross(d, sx)
    draw(a, ms, np.array([sx, sy, d]), title); a.axis("off")
fig.legend(handles=[Patch(color=c, label=l) for _, c, l in items], loc="lower center", ncol=4, fontsize=12)
plt.tight_layout(rect=(0, 0.06, 1, 1)); plt.savefig(sys.argv[1], dpi=80)
