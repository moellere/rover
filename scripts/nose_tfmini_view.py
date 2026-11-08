import subprocess, sys, tempfile, numpy as np
sys.path.insert(0, "scripts")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from stl import mesh
from nose_assembly_views import draw, SCAD, OPENSCAD
items = [("t_body", (0.25, 0.45, 0.85), "nose module: mounting plate (ears bolt to its front face, M2 x2, 36 mm apart)"),
         ("t_tfmini", (0.15, 0.15, 0.15), "TFMini (body + ears, as modelled)")]
ms = []
with tempfile.TemporaryDirectory() as t:
    for p, c, l in items:
        f = f"{t}/{p}.stl"; subprocess.run([OPENSCAD, "-D", f'part="{p}"', "-o", f, SCAD], check=True, capture_output=True)
        ms.append((mesh.Mesh.from_file(f), np.array(c), l))
fig, ax = plt.subplots(1, 3, figsize=(22, 7.5))
def iso(az, el):
    az, el = np.radians(az), np.radians(el)
    d = np.array([np.sin(az) * np.cos(el), np.cos(az) * np.cos(el), np.sin(el)])
    sx = np.cross([0, 0, 1], d); sx /= np.linalg.norm(sx); return np.array([sx, np.cross(d, sx), d])
draw(ax[0], ms, iso(35, 25), "from AHEAD-right, above"); ax[0].axis("off")
draw(ax[1], [ms[0]], iso(180 + 30, 20), "plate alone, from BEHIND-left (Grover side): the two M2 holes"); ax[1].axis("off")
draw(ax[2], ms, np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0.0]]), "SIDE from Grover's right (forward = right)")
ax[2].axhline(55, color="gray", ls="--"); ax[2].text(-18, 55.5, "acrylic underside"); ax[2].set_xlabel("y mm ahead of acrylic edge"); ax[2].set_ylabel("z mm"); ax[2].grid(alpha=.3)
fig.legend(handles=[Patch(color=c, label=l) for _, c, l in items], loc="lower center", ncol=2, fontsize=12)
plt.tight_layout(rect=(0, 0.07, 1, 1)); plt.savefig(sys.argv[1], dpi=80)
