// Driver tray: the two DRV8871 motor drivers and the LM2596 buck on one
// plate, in the L298N's old place on the acrylic deck, under the battery
// cradle (2026-10-31). The tray is its own drill template: set it in place,
// mark the acrylic through the four corner holes, drill, bolt it down (Enoch:
// "I can drill any holes needed").
//
// Layout, seen from above (+Y forward, +X to Grover's right):
//   front - the buck, lengthwise across, IN end at the right... see buck_flip;
//           the BMS sits at the front of the battery pocket, so its leads
//           reach the buck's IN first.
//   rear  - the two DRV8871s side by side, screw terminals facing the REAR
//           (motor and power leads), header edges facing forward to the buck;
//           turned this way so the tray is 52 mm wide - the posts leave only
//           ~57 mm between them (64 mm centres, ~7 mm posts).
// Every board sits on 5 mm standoffs at its holes (v2 margin; v1's 3 mm clears
// the DRV8871's ~2 mm terminal pins by ~1 mm and is fine as printed), with a
// relief slot under each driver's terminal-pin row, M3 screws into the standoffs (self-tapping in PETG).
//
// Measured (Enoch, 10-31): DRV8871 22 x 26 mm, two 3.2 mm holes on the header
// edge 13 mm apart edge-to-edge (16.2 mm centres) - slotted +/-1 mm along that
// edge as he asked; LM2596 21 x 44 mm, two diagonal 3.2 mm holes at
// (2.4, 5.6) and (19.2, 35.9) mm from its OUT- corner (confirmed).
//
// Render: openscad -o driver-tray.stl driver-tray.scad
// Print:  flat, standoffs up, no supports, no brim.

plate_t   = 3;
margin    = 2;
corner_r  = 3;
m3_clear  = 3.4;   // tray-to-acrylic bolts
m3_pilot  = 2.6;   // standoff pilot for an M3 screw (self-taps PETG)
stand_h   = 5;     // v2 margin: the DRV8871 terminal pins stick out ~2 mm (Enoch, 10-31) - v1's 3 mm already clears them by ~1 mm
stand_d   = 6.5;

// DRV8871
drv_l     = 26;    // terminal edge -> header edge (along X here)
drv_w     = 22;    // along Y
drv_hole_c = 16.2; // hole centres along the header edge: 13 mm edge-to-edge + 3.2 mm holes (Enoch corrected 4 -> 3.2, 10-31); v1 printed at 17, inside the +/-1 slots
drv_hole_in = 2.8; // hole centre in from the header edge
drv_slot  = 1;     // +/- along the header edge
drv_gap   = 4;     // between the two boards (wire gap)

// LM2596
buck_l    = 44;    // along X here
buck_w    = 21;    // along Y
// holes in the board's own frame: x across its 21 mm, y along its 44 mm,
// origin at the OUT- corner
buck_h1   = [2.4, 5.6];
buck_h2   = [19.2, 35.9];
buck_slot = 1;

gap_y     = 5;     // between the buck and the drivers
rear_tab  = 7;     // strip behind the drivers for the rear mounting bolts
front_tab = 7;     // strip ahead of the buck for the front mounting bolts

tray_x = 2 * drv_w + drv_gap + 2 * margin;                 // 52
tray_y = rear_tab + margin + drv_l + gap_y + buck_w + margin + front_tab;   // 70

$fn = 32;

// board origins (lower-left corner of each board, plate frame centred in X)
drv_y0  = -tray_y / 2 + rear_tab + margin;     // drivers at the rear (-Y), ahead of the tab
buck_y0 = drv_y0 + drv_l + gap_y;              // buck in front
buck_x0 = -buck_l / 2;

module rounded(x, y, h) {
  linear_extrude(h) offset(r = corner_r) offset(delta = -corner_r) square([x, y], center = true);
}

module slot_hole(d, len, h) {   // slot along Y, total travel 2*len
  hull() for (dy = [-len, len]) translate([0, dy, 0]) cylinder(d = d, h = h);
}

// DRV8871 hole centres: header edge faces forward (+Y), holes along it
function drv_cx(side) = side * (drv_gap / 2 + drv_w / 2);
function drv_holes(side) = [ for (dx = [-drv_hole_c / 2, drv_hole_c / 2])
  [drv_cx(side) + dx, drv_y0 + drv_l - drv_hole_in] ];

// buck hole centres: board rotated so its 44 mm runs along X
function buck_holes() = [ for (h = [buck_h1, buck_h2])
  [buck_x0 + h[1], buck_y0 + h[0]] ];

module tray() {
  difference() {
    union() {
      rounded(tray_x, tray_y, plate_t);
      for (s = [-1, 1]) for (p = drv_holes(s))
        translate([p[0], p[1], 0]) hull() for (dx = [-drv_slot, drv_slot])
          translate([dx, 0, 0]) cylinder(d = stand_d, h = plate_t + stand_h);
      for (p = buck_holes())
        translate([p[0], p[1], 0]) hull() for (dx = [-buck_slot, buck_slot])
          translate([dx, 0, 0]) cylinder(d = stand_d, h = plate_t + stand_h);
    }
    // standoff pilots, slotted
    for (s = [-1, 1]) for (p = drv_holes(s))
      translate([p[0], p[1], -1]) hull() for (dx = [-drv_slot, drv_slot])
        translate([dx, 0, 0]) cylinder(d = m3_pilot, h = plate_t + stand_h + 2);
    for (p = buck_holes())
      translate([p[0], p[1], -1]) hull() for (dx = [-buck_slot, buck_slot])
        translate([dx, 0, 0]) cylinder(d = m3_pilot, h = plate_t + stand_h + 2);
    // tray-to-acrylic holes (the drill template): the front pair beside the
    // buck's ends, the rear pair in the tab behind the drivers - none under a board
    for (sx = [-1, 1]) {
      translate([sx * (tray_x / 2 - 8), tray_y / 2 - front_tab / 2, -1]) cylinder(d = m3_clear, h = plate_t + 2);
      translate([sx * (tray_x / 2 - 8), -tray_y / 2 + rear_tab / 2, -1]) cylinder(d = m3_clear, h = plate_t + 2);
    }
    // relief under each driver's screw-terminal pin row (at its rear edge), so
    // the ~3 mm pins can never bottom on the plate
    for (s = [-1, 1])
      translate([drv_cx(s) - (drv_w - 4) / 2, drv_y0 + 1, -1]) cube([drv_w - 4, 5, plate_t + 2]);
    // wire gap between the drivers' headers: a slot through the plate for
    // the logic leads to drop / rise without crossing the boards
    translate([-drv_gap / 2 + 0.5, drv_y0 + 3, -1]) cube([drv_gap - 1, drv_l - 6, plate_t + 2]);
  }
}

module ghosts() {   // board outlines for checking, not printed
  %for (s = [-1, 1]) translate([drv_cx(s) - drv_w / 2, drv_y0, plate_t + stand_h])
    cube([drv_w, drv_l, 1.6]);
  %translate([buck_x0, buck_y0, plate_t + stand_h]) cube([buck_l, buck_w, 1.6]);
}

tray();
ghosts();
