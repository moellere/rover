"""Assembly drawing of the nose module with its sensors, servos and wiring (2026-11-07).

Headless OpenSCAD can't render PNGs here, so this exports one STL per item
(hardware/nose-module.scad's `asm_*` parts), colours them and draws an
isometric view plus top and side views with a painter's sort in matplotlib.

    uv run --with numpy-stl --with matplotlib python scripts/nose_assembly_views.py OUT.png [--context]

--context adds Grover's front end (tracks, beams, acrylic, deck) and the dock, approximately.
"""
import os
import subprocess
import sys
import tempfile

import matplotlib
import numpy as np
from stl import mesh

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAD = os.path.join(ROOT, "hardware", "nose-module.scad")
OPENSCAD = os.environ.get("OPENSCAD", os.path.expanduser("~/.local/bin/openscad"))

CONTEXT = [
    ("ctx_grover", (0.72, 0.72, 0.72), "Grover: tracks, tread beams, acrylic, spine deck (approx.)"),
    ("ctx_dock", (0.9, 0.85, 0.7), "dock base and rollers (approx.)"),
]
ITEMS = [  # part, colour, legend
    ("body", (0.25, 0.45, 0.85), "nose module (printed, blue PETG)"),
    ("asm_arms", (0.45, 0.65, 0.95), "contact arms + pads (printed)"),
    ("asm_tfmini", (0.15, 0.15, 0.15), "TFMini"),
    ("asm_cliff", (0.1, 0.55, 0.25), "cliff FL / FR (TCRT5000 on HW-870)"),
    ("asm_servo", (0.35, 0.35, 0.40), "SG90 servos"),
    ("asm_w_tfmini", (0.95, 0.75, 0.1), "TFMini lead (4 wire, to spine deck)"),
    ("asm_w_cliff", (0.6, 0.2, 0.8), "cliff leads (3 wire each: 5 V, GND, DO)"),
    ("asm_w_servo", (0.95, 0.45, 0.1), "servo leads (3 wire each: 5 V, GND, signal)"),
    ("asm_w_pad", (0.85, 0.1, 0.1), "pad leads (to the 12 V bus / GND, like the pad bars)"),
]


def load(tmp, items):
    out = []
    for part, col, label in items:
        f = os.path.join(tmp, part + ".stl")
        subprocess.run([OPENSCAD, "-D", f'part="{part}"', "-o", f, SCAD], check=True, capture_output=True)
        out.append((mesh.Mesh.from_file(f), np.array(col), label))
    return out


def draw(ax, meshes, R, title, light=np.array([0.3, -0.5, 0.8])):
    """R: 3x3, rows = screen x, screen y, depth (toward the viewer)."""
    polys, cols, depth = [], [], []
    light = light / np.linalg.norm(light)
    for m, col, _ in meshes:
        v = m.vectors @ R.T
        n = m.normals / (np.linalg.norm(m.normals, axis=1, keepdims=True) + 1e-9)
        shade = 0.45 + 0.55 * np.abs(n @ light)
        polys.append(v[:, :, :2]); depth.append(v[:, :, 2].mean(1))
        cols.append(np.clip(col[None, :] * shade[:, None], 0, 1))
    polys, cols, depth = np.concatenate(polys), np.concatenate(cols), np.concatenate(depth)
    o = np.argsort(depth)
    ax.add_collection(PolyCollection(polys[o], facecolors=cols[o], edgecolors="none"))
    ax.autoscale(); ax.set_aspect("equal"); ax.set_title(title, fontsize=13)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "nose-module-assembly.png"
    items = ITEMS + (CONTEXT if "--context" in sys.argv else [])
    with tempfile.TemporaryDirectory() as tmp:
        meshes = load(tmp, items)
    fig = plt.figure(figsize=(22, 13))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 1])
    # isometric: from ahead, Grover's right and above
    az, el = np.radians(35), np.radians(28)
    # viewer direction d (from object toward eye): ahead (+y), right (+x), up
    d = np.array([np.sin(az) * np.cos(el), np.cos(az) * np.cos(el), np.sin(el)])
    sx = np.cross([0, 0, 1], d); sx /= np.linalg.norm(sx)
    sy = np.cross(d, sx)
    a0 = fig.add_subplot(gs[0, :]); draw(a0, meshes, np.array([sx, sy, d]),
                                         "ISOMETRIC - from ahead of Grover, his RIGHT side nearest, arms lowered onto the rollers")
    a0.axis("off")
    fig.legend(handles=[Patch(color=c, label=l) for _, c, l in items], loc="upper left", bbox_to_anchor=(0.02, 0.97), fontsize=12)
    a1 = fig.add_subplot(gs[1, 0]); draw(a1, meshes, np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1.0]]),
                                         "TOP (forward is UP; Grover's LEFT on the left)")
    a1.set_xlabel("x mm (Grover's LEFT <-  -> RIGHT)"); a1.set_ylabel("y mm ahead of the acrylic edge"); a1.grid(alpha=.3)
    a2 = fig.add_subplot(gs[1, 1]); draw(a2, meshes, np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0.0]]),
                                         "SIDE (from Grover's RIGHT; forward is RIGHT)")
    a2.axhline(0, color="k", lw=1); a2.axhline(55, color="gray", ls="--", lw=.8)
    a2.text(-20, 57, "acrylic underside 55", fontsize=9)
    a2.set_xlabel("y mm forward"); a2.set_ylabel("z mm above the bench"); a2.grid(alpha=.3)
    plt.tight_layout(); plt.savefig(out, dpi=80)
    print("wrote", out)


if __name__ == "__main__":
    main()
