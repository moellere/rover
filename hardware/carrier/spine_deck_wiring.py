"""Spine deck wiring diagram (top view, front up) -> spine-deck-wiring.svg / .png.

Pin map from firmware/rover32.yaml; the board is a YD-ESP32-23 (ESP32-S3,
DevKitC-1 2 x 22 pinout) in the same FNK0101, antenna to the front (USB / FNK0101 power jack to the
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

# ESP32-S3 devkit (YD-ESP32-23, DevKitC-1 layout), antenna to the front
dcx, dcy = fx0 + fw / 2, fy0 + fh / 2
pitch = 2.54 * S
py0 = dcy - 10.5 * pitch + 10       # first pin; the antenna sits ahead of the header
dw = 28 * S
dx0, dy0 = dcx - dw / 2, py0 - 44
dh = 21 * pitch + 44 + 16
rect(dx0, dy0, dw, dh, "#14324f", "#0b1e30", rx=5)
rect(dx0 + 18, dy0 + 4, dw - 36, 28, "#b0b7bf", "#777", rx=3)          # antenna / shield
text(dcx, dy0 + 23, "ESP32-S3 rover32", 11, "middle", col="#222", weight="bold")
for ux in (dcx - 34, dcx + 34):                                        # two USB-C, rear
    rect(ux - 14, dy0 + dh - 4, 28, 12, "#c0c0c0", "#777", rx=3)
text(dcx - 34, dy0 + dh + 22, "COM", 9, "middle", col="#ddd")
text(dcx + 34, dy0 + dh + 22, "USB", 9, "middle", col="#ddd")

left_pins = ["3V3", "3V3", "RST", "4", "5", "6", "7", "15", "16", "17", "18", "8", "3", "46",
             "9", "10", "11", "12", "13", "14", "5V", "GND"]
right_pins = ["GND", "TX", "RX", "1", "2", "42", "41", "40", "39", "38", "37", "36", "35",
              "0", "45", "48", "47", "21", "20", "19", "GND", "GND"]
avoid = {"1", "3", "46", "0", "45", "48", "TX", "RX", "20", "19", "35", "36", "37"}
lx, rx_ = dcx - 12.7 * S, dcx + 12.7 * S
P = {}
used = {"3V3", "4", "5", "6", "7", "15", "16", "17", "8", "9", "5V", "2", "42", "41", "40", "39", "38"}
def pin(x, y, n, side, i):
    on = n in used or n == "GND"
    fill = "#ffd54f" if on else "#c0392b" if n in avoid else "#8a8a8a"
    add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{fill}"/>')
    tc = "#fff" if on else "#e8a39b" if n in avoid else "#9fb0c0"
    if side == "L": text(x + 8, y + 4, n, 10, col=tc)
    else: text(x - 8, y + 4, n, 10, "end", col=tc)
    P.setdefault(side + n, (x, y))
for i, n in enumerate(left_pins): pin(lx, py0 + i * pitch, n, "L", i)
for i, n in enumerate(right_pins): pin(rx_, py0 + i * pitch, n, "R", i)

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
# pin per 5-hole row (each row is one node), right half, column 6, rows 3-10
rp = (bh - 44) / 29
def ry(r): return by0 + 22 + r * rp
def cx(c): return bx0 + 46 + c * 17 + (12 if c >= 5 else 0)
gx = cx(6)
rect(gx - 5, ry(3) - 7, 10, ry(10) - ry(3) + 14, "#1e4fa0", "#0d2f66", rx=2)
gpins = {3: "GND", 4: "VIN", 6: "SCL", 7: "SDA"}  # row order illustrative - follow the silkscreen
for r in range(3, 11):
    dot(gx, ry(r), "#0d2f66", 2.6)
    if r in (6, 7): text(gx + 10, ry(r) + 4, gpins[r], 9, "start", col="#0d2f66", weight="bold")
    else: text(gx - 10, ry(r) + 4, gpins.get(r, "-"), 9, "end", col="#0d2f66")
text(gx + 12, ry(8) + 6, "gyro, upright:", 11, "start", col="#0d2f66", weight="bold")
text(gx + 12, ry(9) + 6, "one pin per row", 10, "start", col="#0d2f66")
text(gx + 12, ry(10) + 6, "(per silkscreen)", 9, "start", col="#555")
line([(cx(7), ry(4)), (rail["3V3"], ry(4))], C["v33"], 2)
line([(cx(7), ry(3)), (rail["GNDb"], ry(3))], C["gnd"], 2)
for r in (3, 4): dot(cx(7), ry(r), "#555", 2.4)

# battery divider: 12 V bus -> 100k -> node -> 27k -> GND; node -> GPIO1
dvy = by0 + 300
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
# left header: front / rear sensors, all straight off the pins
LB = 30   # left boxes x
bwid = 228
port = LB + bwid
yFL, yFR, yRL, yRR, yTS = 380, 432, 478, 515, P["L16"][1]
box(LB, yFL - 22, bwid, [("Cliff FL (front-left)", True), ("OUT -> GPIO5", False)], C["sig"])
box(LB, yFR - 22, bwid, [("Cliff FR (front-right)", True), ("OUT -> GPIO6", False)], C["sig"])
box(LB, yRL - 17, bwid, [("Cliff RL - planned, GPIO7", True)], C["plan"], dash=True, h=34)
box(LB, yRR - 17, bwid, [("Cliff RR - planned, GPIO15", True)], C["plan"], dash=True, h=34)
box(LB, yTS - 19, bwid, [("TFMini (Qwiic), bus_b", True), ("SDA 16 / SCL 17, 5 V", False)], C["i2c"])
text(LB, yFL - 40, "SENSORS (front slot; rear cliff bar)", 13, weight="bold", col="#333")
box(LB, 700, bwid, [("Sensor power", True), ("cliff VCC: 3V3 rail (see note)", False),
                    ("TFMini 5V: 5V rail", False), ("all GND: GND rail", False)], "#444")

line([P["L5"], (440, P["L5"][1]), (440, yFL), (port, yFL)], C["sig"])
line([P["L6"], (425, P["L6"][1]), (425, yFR), (port, yFR)], C["sig"])
line([P["L7"], (410, P["L7"][1]), (410, yRL), (port, yRL)], C["plan"], dash=True)
line([P["L15"], (395, P["L15"][1]), (395, yRR), (port, yRR)], C["plan"], dash=True)
line([P["L16"], (port, P["L16"][1])], C["i2c"])
line([P["L17"], (port, P["L17"][1])], C["i2c"])

# 3V3 out -> breadboard 3V3 rail (over the top of the devkit)
line([P["L3V3"], (474, P["L3V3"][1]), (474, 404), (rail["3V3"], 404), (rail["3V3"], by0 + 12)], C["v33"])
# LED data GPIO4 (left header) -> over the top -> 330R on the breadboard
line([P["L4"], (462, P["L4"][1]), (462, 394), (bx0 + 60, 394), (bx0 + 60, lry)], C["led"])
# right header: GND to the gap-side GND rail
line([P["RGND"], (rail["GNDa"], P["RGND"][1])], C["gnd"])
# battery sense GPIO8 (left header) -> over the top -> divider node.
# GPIO1's FNK0101 terminal is welded to GND (10-31 short): never use it.
line([P["L8"], (450, P["L8"][1]), (450, 384), (bx0 + 40, 384), (bx0 + 40, dvy), (rx1, dvy)], C["bat"])
# gyro I2C (bus_c): GPIO2 / GPIO42, straight across to the gyro rows
line([P["R2"], (cx(5) - 9, P["R2"][1]), (cx(5) - 9, ry(6)), (cx(5), ry(6))], C["i2c"])
line([P["R42"], (cx(5), P["R42"][1]), (cx(5), ry(7))], C["i2c"])
for r in (6, 7): dot(cx(5), ry(r), C["i2c"], 2.6)

# drivers + driver GND: down the centre slot to the power deck
PDy = 880
gnd_low = (rx_, py0 + 20 * pitch)
slot = {"41": gx0 + 34, "40": gx0 + 28, "39": gx0 + 22, "38": gx0 + 16, "GNDd": gx0 + 10}
for n in ("41", "40", "39", "38"):
    line([P["R" + n], (slot[n], P["R" + n][1]), (slot[n], PDy)], C["drv"])
line([gnd_low, (slot["GNDd"], gnd_low[1]), (slot["GNDd"], PDy)], C["gnd"])
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
# dock sense GPIO9 (left header) -> down the left side -> power deck divider
line([P["L9"], (380, P["L9"][1]), (380, PDy + 114), (gx0 - 250, PDy + 114)], C["bat"], dash=True)
rect(pdx, PDy, pdw, 195, "#fff5ec", C["drv"], rx=9, sw=2)
text(pdx + 12, PDy + 22, "POWER DECK (below the top plate)", 14, weight="bold", col=C["drv"])
text(pdx + 12, PDy + 44, "Left DRV8871 (left track):  IN1 <- GPIO38   IN2 <- GPIO39 (firmware swaps them)   GND <- ESP GND", 12)
text(pdx + 12, PDy + 63, "Right DRV8871 (right track): IN1 <- GPIO40   IN2 <- GPIO41   GND <- ESP GND", 12)
text(pdx + 12, PDy + 186, "DANGER: header VM = 12 V (tied to the POWER terminals). Leave it UNCONNECTED.", 12, weight="bold", col="#d62828")
text(pdx + 12, PDy + 82, "Buck OUT (5.29 V) + GND -> breadboard 5V / GND rails", 12)
text(pdx + 12, PDy + 101, "12 V bus (+ Wago) -> 100k -> sense node -> 27k -> GND;  node -> GPIO8", 12)
text(pdx + 12, PDy + 119, "Dock sense: dock pad + (BEFORE D1) -> 100k -> node -> 15k -> GND;  node -> GPIO9", 12, col="#8a5a00")
text(pdx + 12, PDy + 137, "Forward = IN1 high, IN2 PWM (both sides). A track running backward is fixed by", 11, col="#555")
text(pdx + 12, PDy + 152, "swapping its IN1/IN2 pins in firmware, not the wires.", 11, col="#555")
text(pdx + 12, PDy + 169, "Wires reach it down the centre slot (signals) and past the breadboard's rear end (power).", 11, col="#555")

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
rect(nx, ny, 350, 258, "#fffbe6", "#c9a227", rx=8)
text(nx + 12, ny + 24, "Notes", 14, weight="bold")
for i, s in enumerate([
        "Cliff VCC on 3V3: the HW-870's output pulls up",
        "to its VCC, so on 5 V it would drive the ESP32",
        "input above 3.3 V.",
        "Gyro: one pin per breadboard row; wire",
        "VIN/GND/SDA/SCL by its silkscreen;",
        "yaw is still the chip's +Z (hand test 11-01).",
        "Red pins: avoid - 0/3/45/46 strapping, 19/20",
        "native USB, TX/RX CH343, 35-37 PSRAM, 48 RGB;",
        "GPIO1: its FNK0101 terminal is welded to GND.",
        "Free: 10-14, 18, 21, 47.",
        "USB (either port): never with the pack connected."]):
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
