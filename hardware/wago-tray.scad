// Wago tray: holds the two Wago 221-415 lever connectors that make Grover's
// 12 V bus (+12 V and GND), side by side at the front of the acrylic deck,
// between the front posts and ahead of the driver tray (Enoch's layout,
// 2026-10-31). The bridge between them sits over the acrylic's centre
// cut-out and keeps an opening there for the BMS leads to come through.
//
// Each Wago presses into a pocket (Enoch: press fit, no zip ties): crush ribs on
// the two short end walls grip its 30 mm length, and 2 mm side rails locate it
// across - low enough to stay under the wire entries on one long side and the
// levers on the other, which both need clearance (levers lift up - make the connections before the battery
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
fit      = 0.6;     // on the length: clearance between the end walls; the ribs take it up
rib_h    = 0.45;    // crush ribs: stand proud of each end wall by this much
rib_w    = 1.2;
rail_h   = 2;       // side rails along the long sides
rail_t   = 1.2;
side_fit = 0.3;
floor_t  = 2;
end_h    = 6;       // end walls (Wago is ~8.5 tall)
end_t    = 2;
gap      = 19;      // between the two Wagos (over the acrylic cut-out)
open_w   = 12;      // BMS-lead opening in the bridge
open_d   = 9;
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
        for (e = [-1, 1]) {   // end walls of each pocket, with two crush ribs each
          translate([cx + e * (pocket_l / 2 + end_t / 2) - end_t / 2, -depth / 2, 0])
            cube([end_t, depth, floor_t + end_h]);
          for (dy = [-5, 5])
            translate([cx + e * (pocket_l / 2) - (e > 0 ? rib_h : 0), dy - rib_w / 2, floor_t])
              cube([rib_h, rib_w, end_h]);
        }
        for (sy = [-1, 1])   // low side rails
          translate([cx - pocket_l / 2, sy > 0 ? wago_w / 2 + side_fit / 2 : -wago_w / 2 - side_fit / 2 - rail_t, 0])
            cube([pocket_l, rail_t, floor_t + rail_h]);
      }
    }
    // BMS-lead opening in the bridge
    translate([-open_w / 2, -open_d / 2, -1]) cube([open_w, open_d, floor_t + 2]);
    // drill-template holes either side of the opening
    for (dy = [-1, 1]) translate([0, dy * (open_d / 2 + 3.5), -1]) cylinder(d = m3_clear, h = floor_t + 2);
  }
}

module ghosts() {   // the two Wagos, for checking
  for (s = [-1, 1]) %translate([s * (gap / 2 + cell_x / 2) - wago_l / 2, -wago_w / 2, floor_t]) cube([wago_l, wago_w, 8.5]);
}

tray();
ghosts();
