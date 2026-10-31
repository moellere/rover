// Wago tray: holds the two Wago 221-415 lever connectors that make Grover's
// 12 V bus (+12 V and GND), side by side at the front of the acrylic deck,
// between the front posts and ahead of the driver tray (Enoch's layout,
// 2026-10-31). The bridge between them sits over the acrylic's centre
// cut-out and keeps an opening there for the BMS leads to come through.
//
// Each Wago drops into a pocket held by its two short end walls (snug on the
// 30 mm length) and a zip tie through the floor slot under it. The long sides
// stay open: one side is the wire entries, the other the levers, and both
// need clearance (levers lift up - make the connections before the battery
// cradle goes on). The tray is its own drill template: two M3 holes in the
// bridge, either side of the opening.
//
// Measured: Wago 18 x 30 mm (Enoch, 10-31), ~8.5 mm tall; gap between them in
// his layout ~19 mm.
//
// Render: openscad -o wago-tray.stl wago-tray.scad
// Print:  floor down, no supports, no brim.

wago_l   = 30.0;
wago_w   = 18.0;
fit      = 0.4;     // on the length: snug between the end walls
floor_t  = 2;
end_h    = 6;       // end walls (Wago is ~8.5 tall)
end_t    = 2;
gap      = 19;      // between the two Wagos (over the acrylic cut-out)
open_w   = 12;      // BMS-lead opening in the bridge
open_d   = 9;
tie_w    = 3.5;     // zip-tie slot
tie_l    = 1.8;
m3_clear = 3.4;
depth    = wago_w + 4;   // tray front-to-back

pocket_l = wago_l + fit;
cell_x   = pocket_l + 2 * end_t;
total_x  = 2 * cell_x + gap;

$fn = 32;

module tray() {
  difference() {
    union() {
      translate([-total_x / 2, -depth / 2, 0]) cube([total_x, depth, floor_t]);
      for (s = [-1, 1]) {
        cx = s * (gap / 2 + cell_x / 2);
        for (e = [-1, 1])   // end walls of each pocket
          translate([cx + e * (pocket_l / 2 + end_t / 2) - end_t / 2, -depth / 2, 0])
            cube([end_t, depth, floor_t + end_h]);
      }
    }
    // BMS-lead opening in the bridge
    translate([-open_w / 2, -open_d / 2, -1]) cube([open_w, open_d, floor_t + 2]);
    // drill-template holes either side of the opening
    for (dy = [-1, 1]) translate([0, dy * (open_d / 2 + 3.5), -1]) cylinder(d = m3_clear, h = floor_t + 2);
    // zip-tie slots under each Wago, across its 18 mm width
    for (s = [-1, 1]) {
      cx = s * (gap / 2 + cell_x / 2);
      for (dx = [-6, 6]) translate([cx + dx - tie_l / 2, -wago_w / 2 - 1, -1]) cube([tie_l, 1.2, floor_t + 2]);
      for (dx = [-6, 6]) translate([cx + dx - tie_l / 2, wago_w / 2 - 0.2, -1]) cube([tie_l, 1.2, floor_t + 2]);
    }
  }
}

module ghosts() {   // the two Wagos, for checking
  for (s = [-1, 1]) %translate([s * (gap / 2 + cell_x / 2) - wago_l / 2, -wago_w / 2, floor_t]) cube([wago_l, wago_w, 8.5]);
}

tray();
ghosts();
