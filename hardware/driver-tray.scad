// Driver tray v3: Grover's power deck under the battery cradle (2026-10-31).
// The two DRV8871 motor drivers, the LM2596 buck and the two Wago 221-415
// lever connectors that make the 12 V bus, on one plate in the L298N's old
// place on the acrylic. The tray is its own drill template: set it between
// the posts, mark the acrylic through the four holes, drill, bolt it down.
//
// Layout, seen from above (+Y forward, +X to Grover's right) - Enoch's mock-up
// (v3), so the 12 V parts sit together:
//   front - the buck LENGTHWISE: OUT (5 V) forward, IN at the rear;
//           the Wagos lengthwise either side of it, + on the left and GND on
//           the right, levers facing OUTWARD (reachable from the sides with
//           the cradle on), wire entries facing the buck.
//   rear  - the two DRV8871s side by side, screw terminals to the REAR (motor
//           and power leads), header edges forward; ~3 cm from the Wagos.
// The posts stand only at the four corners (64 x 96 mm centres), so only the
// ends must stay narrow (<~57 mm); the middle is wider for the Wagos, and the
// narrow spine runs on forward between the front posts for the BMS-lead opening.
//
// Boards on 5 mm standoffs at their holes (solder joints underneath), slotted
// +/-1 mm; relief under each driver's terminal-pin row; wire slot between the
// drivers. Wagos press-fit: crush ribs on the pocket ends, 2 mm side rails.
//
// Measured (Enoch, 10-31): DRV8871 22 x 26 mm, two 3.2 mm holes on the header
// edge, 16.2 mm centres; LM2596 21 x 44 mm, diagonal 3.2 mm holes at
// (2.4, 5.6) and (19.2, 35.9) mm from its OUT- corner; Wago 18 x 30 mm.
// v1 (7e81c54605) had the buck diagonal mirrored; v2 put the Wagos across the
// front; both superseded by this layout.
//
// Render: openscad -o driver-tray.stl driver-tray.scad
// Print:  flat, standoffs up, no supports, no brim.

plate_t  = 3;
corner_r = 3;
m3_clear = 3.4;
m3_pilot = 2.6;
stand_h  = 5;
stand_d  = 6.5;
slot     = 1;      // +/- on every board hole

// DRV8871
drv_l = 26; drv_w = 22; drv_hole_c = 16.2; drv_hole_in = 2.8; drv_gap = 4;
// LM2596 (board frame: x across its 21 mm, y along its 44 mm, origin OUT- corner)
buck_l = 44; buck_w = 21; buck_h1 = [2.4, 5.6]; buck_h2 = [19.2, 35.9];
// Wago
wago_l = 30; wago_w = 18; wfit = 0.6; rib_h = 0.45; rib_w = 1.2;
rail_h = 2; rail_t = 1.2; side_fit = 0.3; end_t = 2; end_h = 6;

// stations along Y (rear -> front)
y_rear   = -43;
rear_tab = 7;
y_drv0   = y_rear + rear_tab + 2;           // drivers' terminal (rear) edge
y_drv1   = y_drv0 + drv_l;                  // their header edge
y_buck0  = y_drv1 + 5;                      // buck IN end
y_buck1  = y_buck0 + buck_l;                // buck OUT end
y_wing1  = y_buck1 + 2;                     // the wide wings end here (behind the front posts)
y_front  = y_buck1 + 11;                    // the narrow spine runs on, between the front posts, for the BMS-lead opening

narrow_x = 2 * drv_w + drv_gap + 4;         // 52: the ends, between the posts
wago_cx  = buck_w / 2 + 3 + rail_t + side_fit / 2 + wago_w / 2;    // Wago centre lines
wide_x   = 2 * (wago_cx + wago_w / 2 + side_fit / 2 + rail_t) + 2;  // ~70 mid-section
pocket_l = wago_l + wfit;
y_wago0  = y_buck0;                         // Wagos level with the buck's IN end
y_wago1  = y_wago0 + pocket_l + 2 * end_t;

$fn = 32;

module rrect(x0, y0, x1, y1, h) {
  linear_extrude(h) offset(r = corner_r) offset(delta = -corner_r)
    translate([x0, y0]) square([x1 - x0, y1 - y0]);
}

function drv_cx(s) = s * (drv_gap / 2 + drv_w / 2);
function drv_holes(s) = [ for (dx = [-drv_hole_c / 2, drv_hole_c / 2]) [drv_cx(s) + dx, y_drv1 - drv_hole_in] ];
// buck lengthwise, OUT forward, OUT- corner at front-right (Enoch's mock-up)
function buck_holes() = [ for (h = [buck_h1, buck_h2]) [buck_w / 2 - h[0], y_buck1 - h[1]] ];

module standoff(p, along_x) {
  translate([p[0], p[1], 0]) hull() for (d = [-slot, slot])
    translate(along_x ? [d, 0, 0] : [0, d, 0]) cylinder(d = stand_d, h = plate_t + stand_h);
}
module pilot(p, along_x) {
  translate([p[0], p[1], -1]) hull() for (d = [-slot, slot])
    translate(along_x ? [d, 0, 0] : [0, d, 0]) cylinder(d = m3_pilot, h = plate_t + stand_h + 2);
}

module wago_pocket(cx) {
  // end walls (front and rear) with crush ribs, low rails along both long sides
  for (e = [-1, 1]) {
    yc = (y_wago0 + y_wago1) / 2 + e * (pocket_l / 2 + end_t / 2);
    translate([cx - wago_w / 2 - side_fit / 2 - rail_t, yc - end_t / 2, 0])
      cube([wago_w + side_fit + 2 * rail_t, end_t, plate_t + end_h]);
    for (dx = [-5, 5])
      translate([cx + dx - rib_w / 2, (y_wago0 + y_wago1) / 2 + e * pocket_l / 2 - (e > 0 ? rib_h : 0), plate_t])
        cube([rib_w, rib_h, end_h]);
  }
  for (sx = [-1, 1])
    translate([cx + (sx > 0 ? wago_w / 2 + side_fit / 2 : -wago_w / 2 - side_fit / 2 - rail_t), y_wago0 + end_t, 0])
      cube([rail_t, pocket_l, plate_t + rail_h]);
}

module tray() {
  difference() {
    union() {
      rrect(-narrow_x / 2, y_rear, narrow_x / 2, y_front, plate_t);              // spine
      rrect(-wide_x / 2, y_wago0 - 2, wide_x / 2, y_wing1, plate_t);             // Wago wings
      for (s = [-1, 1]) for (p = drv_holes(s)) standoff(p, true);
      for (p = buck_holes()) standoff(p, false);
      for (s = [-1, 1]) wago_pocket(s * wago_cx);
    }
    for (s = [-1, 1]) for (p = drv_holes(s)) pilot(p, true);
    for (p = buck_holes()) pilot(p, false);
    // relief under each driver's terminal-pin row
    for (s = [-1, 1]) translate([drv_cx(s) - (drv_w - 4) / 2, y_drv0 + 1, -1]) cube([drv_w - 4, 5, plate_t + 2]);
    // wire slot between the drivers
    translate([-drv_gap / 2 + 0.5, y_drv0 + 3, -1]) cube([drv_gap - 1, drv_l - 6, plate_t + 2]);
    // drill-template holes: rear tab pair, front wing pair (ahead of the Wagos)
    for (sx = [-1, 1]) {
      translate([sx * (narrow_x / 2 - 8), y_rear + rear_tab / 2, -1]) cylinder(d = m3_clear, h = plate_t + 2);
      translate([sx * wago_cx, (y_wago1 + y_wing1) / 2, -1]) cylinder(d = m3_clear, h = plate_t + 2);
    }
    // BMS-lead opening ahead of the buck's OUT end, in the spine (the BMS sits at
    // the front of the battery pocket and its leads drop here)
    translate([-7, y_buck1 + 2.5, -1]) cube([14, 7, plate_t + 2]);
  }
}

module ghosts() {
  %for (s = [-1, 1]) translate([drv_cx(s) - drv_w / 2, y_drv0, plate_t + stand_h]) cube([drv_w, drv_l, 1.6]);
  %translate([-buck_w / 2, y_buck0, plate_t + stand_h]) cube([buck_w, buck_l, 1.6]);
  %for (s = [-1, 1]) translate([s * wago_cx - wago_w / 2, y_wago0 + end_t + wfit / 2, plate_t]) cube([wago_w, wago_l, 8.5]);
}

tray();
ghosts();
