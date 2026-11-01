"""Spine deck wiring diagram (top view, front up) -> spine-deck-wiring.svg / .png.

Pin map from firmware/rover32.yaml; devkit pinout is the standard 38-pin
ESP32-WROOM-32D devkit, antenna to the front (USB / FNK0101 power jack to the
rear, as the top plate mounts it). Board sizes to scale (5 px/mm): FNK0101
87.6 x 83.2, half breadboard 54 x 82, 8 mm gap (top-plate.scad).

Run: uv run --with cairosvg python spine_deck_wiring.py
"""
import os

S = 5.0  # px per mm
W, H = 1500, 1080
out = []
add = out.append

C = dict(sig="#1f8a3b", i2c="#1f5fbf", drv="#c2410c", led="#8e3fbf",
         v5="#d62828", v33="#e8930c", gnd="#222222", bat="#b8860b", plan="#7a7a7a")

def line(pts, col, w=2.6, dash=False, halo=True):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d = ' stroke-dasharray="7 5"' if dash else ""
    if halo:
        add(f'<polyline points="{p}" fill="none" stroke="#fff" stroke-width="{w + 4}" stroke-linejoin="round"/>')
    add(f'<polyline points="{p}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="round"{d}/>')

def text(x, y, s, size=13, anchor="start", col="#111", weight="normal"):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{col}" '
        f'font-family="DejaVu Sans, Arial, sans-serif" font-weight="{weight}">{s}</text>')

def rect(x, y, w, h, fill, stroke="#333", rx=6, sw=1.5, dash=False):
    d = ' stroke-dasharray="6 4"' if dash else ""
    add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

def dot(x, y, col, r=4.5):
    add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" stroke="#fff" stroke-width="1.2"/>')

def box(x, y, w, lines, col, dash=False, h=None):
    h = h or 10 + 17 * len(lines)
    rect(x, y, w, h, "#fff", col, rx=7, sw=2, dash=dash)
    for i, (s, b) in enumerate(lines):
        text(x + 8, y + 19 + 17 * i, s, 13 if b else 12, weight="bold" if b else "normal",
             col=col if b else "#222")
    return h

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
rect(0, 0, W, H, "#fbfaf7", "none", rx=0)
text(W / 2, 38, "Grover - spine deck wiring (top view, front up)", 24, "middle", weight="bold")
text(W / 2, 62, "rover32 on the Freenove FNK0101, half breadboard beside it; wires off the deck go to the "
     "front sensors (left), the LED chain (top) and the power deck below (bottom)", 13, "middle", col="#555")

# ---- top plate, boards ------------------------------------------------------
fx0, fy0 = 330, 370
fw, fh = 87.6 * S, 83.2 * S
gx0 = fx0 + fw                       # gap / centre cable slot
bx0, bw, bh = gx0 + 8 * S, 54 * S, 82 * S
by0 = fy0 + 3 * S
rect(fx0 - 15, fy0 - 15, (bx0 + bw + 15) - (fx0 - 15), fh + 40, "#dde7f5", "#5b7db1", rx=14, sw=2)   # top plate
rect(fx0 + fw / 2 + 25, 240, 400, fy0 - 15 - 240 + 1, "#dde7f5", "#5b7db1", rx=10, sw=2)             # camera tab
text(fx0 + fw / 2 + 225, 268, "camera perch (front tab)", 13, "middle", col="#3b5b8f")
text(fx0 - 5, fy0 + fh + 40, "top plate (blue PETG)", 12, col="#3b5b8f")
# centre slot between the boards
rect(gx0 + 15, fy0 + fh / 2 - 150, 10, 300, "#9fb3d1", "#5b7db1", rx=4, sw=1)
text(gx0 + 20, fy0 + fh / 2 + 172, "centre slot", 11, "middle", col="#3b5b8f")

rect(fx0, fy0, fw, fh, "#1c1c1c", "#000", rx=8)                        # FNK0101
for x in (fx0 + 8, fx0 + fw - 28):                                     # terminal strips
    rect(x, fy0 + 30, 20, fh - 60, "#2e7d32", "#1b5e20", rx=3, sw=1)
text(fx0 + fw / 2, fy0 + fh - 12, "Freenove FNK0101", 13, "middle", col="#ddd", weight="bold")
rect(fx0 + fw - 70, fy0 + fh - 30, 45, 26, "#111", "#555", rx=3)        # barrel jack, rear

# ESP32 devkit, antenna to the front
dcx, dcy = fx0 + fw / 2, fy0 + fh / 2
pitch = 2.54 * S
py0 = dcy - 9 * pitch + 14          # first pin; the antenna sits ahead of the header
dw = 28 * S
dx0, dy0 = dcx - dw / 2, py0 - 44
dh = 18 * pitch + 44 + 16
rect(dx0, dy0, dw, dh, "#14324f", "#0b1e30", rx=5)
rect(dx0 + 18, dy0 + 4, dw - 36, 28, "#b0b7bf", "#777", rx=3)          # antenna / shield
text(dcx, dy0 + 23, "ESP32 rover32", 11, "middle", col="#222", weight="bold")
rect(dcx - 22, dy0 + dh - 4, 44, 16, "#c0c0c0", "#777", rx=3)          # USB
text(dcx, dy0 + dh + 26, "USB (rear) - never with the pack connected", 10, "middle", col="#ddd")

left_pins = ["3V3", "EN", "VP", "VN", "34", "35", "32", "33", "25", "26", "27", "14", "12",
             "GND", "13", "D2", "D3", "CMD", "5V"]
right_pins = ["GND", "23", "22", "TX", "RX", "21", "GND", "19", "18", "5", "17", "16", "4",
              "0", "2", "15", "D1", "D0", "CLK"]
lx, rx_ = dcx - 12.7 * S, dcx + 12.7 * S
P = {}
used = {"3V3", "34", "35", "32", "33", "25", "26", "13", "5V", "23", "22", "21", "19", "18", "5", "4"}
for i, n in enumerate(left_pins):
    y = py0 + i * pitch
    P["L" + n] = (lx, y)
    add(f'<circle cx="{lx:.1f}" cy="{y:.1f}" r="3.2" fill="{"#ffd54f" if n in used or n == "GND" else "#8a8a8a"}"/>')
    text(lx + 8, y + 4, n, 10, col="#fff" if n in used or n == "GND" else "#9fb0c0")
for i, n in enumerate(right_pins):
    y = py0 + i * pitch
    P["R" + n] = (rx_, y)
    add(f'<circle cx="{rx_:.1f}" cy="{y:.1f}" r="3.2" fill="{"#ffd54f" if n in used or n == "GND" else "#8a8a8a"}"/>')
    text(rx_ - 8, y + 4, n, 10, "end", col="#fff" if n in used or n == "GND" else "#9fb0c0")
P["LGND"] = (lx, py0 + 13 * pitch)
P["RGND"] = (rx_, py0 + 0 * pitch)
P["RGND2"] = (rx_, py0 + 6 * pitch)

# breadboard: rails along both long edges, 5V/GND on the gap side, 3V3/GND outboard
rect(bx0, by0, bw, bh, "#f4f1ea", "#9a958a", rx=6)
text(bx0 + bw / 2, by0 - 8, "half breadboard (400)", 12, "middle", col="#555")
rail = {"5V": bx0 + 12, "GNDa": bx0 + 26, "GNDb": bx0 + bw - 26, "3V3": bx0 + bw - 12}
for k, x in rail.items():
    col = C["v5"] if k == "5V" else C["v33"] if k == "3V3" else C["gnd"]
    add(f'<line x1="{x}" y1="{by0 + 10}" x2="{x}" y2="{by0 + bh - 10}" stroke="{col}" stroke-width="3" opacity="0.75"/>')
text(rail["5V"] - 8, by0 + bh + 16, "5V", 11, "middle", col=C["v5"], weight="bold")
text(rail["GNDa"], by0 + bh + 30, "GND", 10, "middle")
text(rail["GNDb"], by0 + bh + 30, "GND", 10, "middle")
text(rail["3V3"], by0 + bh + 16, "3V3", 11, "middle", col=C["v33"], weight="bold")
for r in range(30):                                                    # hole grid
    y = by0 + 22 + r * (bh - 44) / 29
    for c in range(10):
        x = bx0 + 46 + c * 17 + (12 if c >= 5 else 0)
        add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.3" fill="#c9c3b6"/>')
bcx = bx0 + bw / 2

# gyro, upright in the breadboard: its 8 in-line pins run ALONG a column, one
# pin per 5-hole row (each row is one node), right half, column 6
rp = (bh - 44) / 29
def ry(r): return by0 + 22 + r * rp
def cx(c): return bx0 + 46 + c * 17 + (12 if c >= 5 else 0)
gx = cx(6)
rect(gx - 5, ry(1) - 7, 10, ry(8) - ry(1) + 14, "#1e4fa0", "#0d2f66", rx=2)
gpins = {1: "GND", 2: "VIN", 4: "SCL", 5: "SDA"}     # row order illustrative - follow the silkscreen
for r in range(1, 9):
    dot(gx, ry(r), "#0d2f66", 2.6)
    text(gx - 10, ry(r) + 4, gpins.get(r, "-"), 9, "end", col="#0d2f66")
text(gx - 34, ry(6) + 4, "gyro, upright:", 11, "end", col="#0d2f66", weight="bold")
text(gx - 34, ry(7) + 4, "one pin per row", 10, "end", col="#0d2f66")
text(gx - 34, ry(8) + 4, "(order per silkscreen)", 9, "end", col="#555")
line([(cx(7), ry(2)), (rail["3V3"], ry(2))], C["v33"], 2)
line([(cx(7), ry(1)), (rail["GNDb"], ry(1))], C["gnd"], 2)
for r in (1, 2): dot(cx(7), ry(r), "#555", 2.4)

# battery divider: 12 V bus -> 100k -> node -> 27k -> GND; node -> GPIO34
dvy = by0 + 280
def resistor(x, y, label):
    rect(x - 6, y - 16, 12, 32, "#e9d8a6", "#7a6a3a", rx=4, sw=1.2)
    text(x - 10, y + 4, label, 11, "end", col="#5a4a1a", weight="bold")
rx1 = cx(8)
resistor(rx1, dvy - 30, "100k")
resistor(rx1, dvy + 30, "27k")
dot(rx1, dvy, C["bat"], 5)
text(rx1 - 10, dvy - 6, "node", 10, "end", col=C["bat"], weight="bold")
line([(rx1, dvy + 46), (rx1, dvy + 62), (rail["GNDb"], dvy + 62)], C["gnd"], 2)

# LED series resistor
lry = by0 + 372
rect(bx0 + 60, lry - 6, 34, 12, "#e9d8a6", "#7a6a3a", rx=4, sw=1.2)
text(bx0 + 77, lry - 10, "330R", 11, "middle", col="#5a4a1a", weight="bold")

# ---- wires from the devkit ---------------------------------------------------
# left side: front / rear sensors
LB = 30   # left boxes x
bwid = 228
port = LB + bwid
yFL, yFR, yRL, yTS, yRR = 425, 482, 528, 572, 646
h = box(LB, yFL - 22, bwid, [("Cliff FL (front-left)", True), ("OUT -> GPIO35", False)], C["sig"])
box(LB, yFR - 22, bwid, [("Cliff FR (front-right)", True), ("OUT -> GPIO32", False)], C["sig"])
box(LB, yRL - 18, bwid, [("Cliff RL - planned", True)], C["plan"], dash=True, h=34)
box(LB, yTS - 20, bwid, [("TFMini (Qwiic), bus_b", True), ("SDA 25 / SCL 26, 5 V", False)], C["i2c"])
box(LB, yRR - 18, bwid, [("Cliff RR - planned", True)], C["plan"], dash=True, h=34)
text(LB, yFL - 40, "SENSORS (front slot; rear cliff bar)", 13, weight="bold", col="#333")
box(LB, 700, bwid, [("Sensor power", True), ("cliff VCC: 3V3 rail (see note)", False),
                    ("TFMini 5V: 5V rail", False), ("all GND: GND rail", False)], "#444")

line([P["L35"], (440, P["L35"][1]), (440, yFL), (port, yFL)], C["sig"])
line([P["L32"], (425, P["L32"][1]), (425, yFR), (port, yFR)], C["sig"])
line([P["L33"], (410, P["L33"][1]), (410, yRL), (port, yRL)], C["plan"], dash=True)
line([P["L25"], (port, P["L25"][1])], C["i2c"])
line([P["L26"], (port, P["L26"][1])], C["i2c"])
line([P["L13"], (395, P["L13"][1]), (395, yRR), (port, yRR)], C["plan"], dash=True)

# battery sense GPIO34 -> divider node (up and over the devkit)
line([P["L34"], (460, P["L34"][1]), (460, 392), (bx0 + 40, 392), (bx0 + 40, dvy), (rx1, dvy)], C["bat"])
# 3V3 out -> breadboard 3V3 rail
line([P["L3V3"], (474, P["L3V3"][1]), (474, 404), (rail["3V3"], 404), (rail["3V3"], by0 + 12)], C["v33"])
# right side: GND to the gap-side GND rail
line([P["RGND"], (rail["GNDa"], P["RGND"][1])], C["gnd"])

# drivers + driver GND: down the centre slot to the power deck
PDy = 880
slot = {"23": gx0 + 34, "22": gx0 + 28, "GND2": gx0 + 22, "19": gx0 + 16, "18": gx0 + 10}
line([P["R23"], (slot["23"], P["R23"][1]), (slot["23"], PDy)], C["drv"])
line([P["R22"], (slot["22"], P["R22"][1]), (slot["22"], PDy)], C["drv"])
line([P["RGND2"], (slot["GND2"], P["RGND2"][1]), (slot["GND2"], PDy)], C["gnd"])
line([P["R19"], (slot["19"], P["R19"][1]), (slot["19"], PDy)], C["drv"])
line([P["R18"], (slot["18"], P["R18"][1]), (slot["18"], PDy)], C["drv"])
# gyro I2C (bus_c) and LED data cross over the slot wires
line([P["R21"], (cx(8), P["R21"][1]), (cx(8), ry(5)), (cx(7), ry(5))], C["i2c"])
dot(cx(7), ry(5), C["i2c"], 2.6)
line([P["R5"], (cx(9), P["R5"][1]), (cx(9), ry(4)), (cx(7), ry(4))], C["i2c"])
dot(cx(7), ry(4), C["i2c"], 2.6)
line([P["R4"], (bx0 + 60, P["R4"][1]), (bx0 + 60, lry)], C["led"])
# LED chain box (top right) <- 330R
LEDx, LEDy = 1120, 150
box(LEDx, LEDy, 350, [("LED chain (front)", True), ("Din <- GPIO4 via 330R (breadboard)", False),
                      ("headlight L -> R -> status strip (2-7)", False), ("5V and GND from the 5V / GND rails", False)],
    C["led"])
line([(bx0 + 94, lry), (bx0 + bw + 40, lry), (bx0 + bw + 40, LEDy + 60), (LEDx, LEDy + 60)], C["led"])

# 5V: buck -> breadboard 5V rail -> devkit 5V pin
line([(rail["5V"], PDy), (rail["5V"], by0 + bh - 12)], C["v5"])
line([(rail["5V"], by0 + bh - 30), (gx0 - 4, by0 + bh - 30), (gx0 - 4, fy0 + fh + 8), (dx0 - 22, fy0 + fh + 8),
      (dx0 - 22, P["L5V"][1]), P["L5V"]], C["v5"])
# 12 V bus -> 100k (top of divider)
line([(bx0 + 228, PDy), (bx0 + 228, dvy - 60), (rx1, dvy - 60), (rx1, dvy - 46)], C["bat"])

# ---- power deck box (below) ------------------------------------------------
pdx, pdw = gx0 - 250, 650
rect(pdx, PDy, pdw, 195, "#fff5ec", C["drv"], rx=9, sw=2)
text(pdx + 12, PDy + 22, "POWER DECK (below the top plate)", 14, weight="bold", col=C["drv"])
text(pdx + 12, PDy + 44, "Left DRV8871 (left track):  IN1 <- GPIO22   IN2 <- GPIO23   GND <- ESP GND", 12)
text(pdx + 12, PDy + 63, "Right DRV8871 (right track): IN1 <- GPIO19   IN2 <- GPIO18   GND <- ESP GND", 12)
text(pdx + 12, PDy + 186, "DANGER: header VM = 12 V (tied to the POWER terminals). Leave it UNCONNECTED.", 12, weight="bold", col="#d62828")
text(pdx + 12, PDy + 82, "Buck OUT (5.29 V) + GND -> breadboard 5V / GND rails", 12)
text(pdx + 12, PDy + 101, "12 V bus (+ Wago) -> 100k -> sense node -> 27k -> GND;  node -> GPIO34", 12)
text(pdx + 12, PDy + 124, "Forward = IN1 high, IN2 PWM (both sides). A track running backward is fixed by", 11, col="#555")
text(pdx + 12, PDy + 140, "swapping its IN1/IN2 pins in firmware, not the wires.", 11, col="#555")
text(pdx + 12, PDy + 162, "Wires reach it down the centre slot (signals) and past the breadboard's rear end (power).", 11, col="#555")

# ---- legend / notes ----------------------------------------------------------
lgx, lgy = 1120, 330
rect(lgx, lgy, 350, 272, "#fff", "#999", rx=8)
text(lgx + 12, lgy + 24, "Legend", 14, weight="bold")
for i, (k, s) in enumerate([("sig", "cliff sensor signal"), ("i2c", "I2C (TFMini bus_b, gyro bus_c)"),
                            ("drv", "driver inputs"), ("led", "LED data"), ("bat", "battery sense / 12 V"),
                            ("v5", "5 V"), ("v33", "3.3 V"), ("gnd", "GND"), ("plan", "planned (rear cliff bar)")]):
    y = lgy + 48 + i * 24
    add(f'<line x1="{lgx + 14}" y1="{y - 4}" x2="{lgx + 50}" y2="{y - 4}" stroke="{C[k]}" stroke-width="3"'
        f'{" stroke-dasharray=\"7 5\"" if k == "plan" else ""}/>')
    text(lgx + 60, y, s, 12)

nx, ny = 1120, 650
rect(nx, ny, 350, 225, "#fffbe6", "#c9a227", rx=8)
text(nx + 12, ny + 24, "Notes", 14, weight="bold")
for i, s in enumerate([
        "Cliff VCC on 3V3: the HW-870's output pulls up",
        "to its VCC, so on 5 V it would drive the ESP32",
        "input above 3.3 V.",
        "Gyro: one pin per breadboard row; wire",
        "VIN/GND/SDA/SCL by its silkscreen;",
        "yaw axis moves off Z (stands upright).",
        "Pin side: GPIO 34/35 are input-only (fine here).",
        "Unused / avoid: 0, 2, 12, 15 (strapping), 6-11.",
        "Free: 14, 16, 17, 27."]):
    text(nx + 12, ny + 48 + i * 19, s, 12)

text(30, H - 18, "<- Grover's LEFT", 13, col="#555", weight="bold")
text(W - 30, H - 18, "Grover's RIGHT ->", 13, "end", col="#555", weight="bold")
add(f'<path d="M {W - 60} 120 l 0 -50 m -10 14 l 10 -14 l 10 14" stroke="#333" stroke-width="3" fill="none"/>')
text(W - 60, 140, "FRONT", 12, "middle", weight="bold")
add("</svg>")

here = os.path.dirname(os.path.abspath(__file__))
svg = "\n".join(out)
open(os.path.join(here, "spine-deck-wiring.svg"), "w").write(svg)
try:
    import cairosvg
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(here, "spine-deck-wiring.png"))
except ImportError:
    pass
