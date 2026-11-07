// Nose module v1 (2026-11-07, DRAFT for Enoch's review - not sliced): one printed
// part replacing the TFMini bracket, both front cliff mounts, the bumper bar and
// the pad plates. Carries:
//   - the TFMini, lens centre 53 mm up, front face 42 mm ahead of the acrylic
//     (where it is now, Enoch);
//   - both front cliff sensors (HW-870/TCRT5000) on wings in front of the
//     tracks, the TCRT5000 BODY held in a socket (today it hangs on its leads
//     and they bent - Enoch's photo), raised from ~6 mm to `cliff_face_z`, with a
//     skid tab either side reaching 3 mm lower;
//   - a bumper crossbar, the front-most hard stop;
//   - two SG90 servos, one per side, swinging contact arms: Grover stops with
//     the bumper at the dock's tip and the arms lower sprung pads onto the
//     rollers 50 mm further on (90 mm apart c-c, 5 mm wide fore-aft, 19 mm dia,
//     ~7 mm proud - Enoch). No climbing, no dock mode, retry on a miss.
//   Pads: copper runs FORE-AFT, 8 mm apart (a 19 mm roller's crown reaches a
//   wire ~4 mm off-centre with the wire 1 mm proud), ~24 mm long - so about
//   +/-12 mm of tolerance both ways.
//
// Mounting: under the acrylic through the front row's holes 1, 3, 7, 9 (8 mm
// pitch, hole 5 on the centreline -> x = +/-16, +/-32), the foot running back
// under the plate behind the bolts so the nose can't pitch down.
//
// Frame: +y FORWARD, +x Grover's RIGHT, z up from the bench (right-handed:
// forward x up = right). Origin: centreline, at the acrylic's front edge.
// Measured (Enoch, 11-07): acrylic underside 55 mm up, ~2 mm thick; its front
// edge ~10 mm ahead of the tracks' first ground contact; TFMini lens 53 mm up.
// UNMEASURED: `row_y` (front hole row behind the edge) - MEASURE before slicing.
//
// Render: openscad -o nose-module.stl nose-module.scad
// Print:  foot face down (as modelled, flipped), tree supports for the arms'
//         bosses if needed - TBD after review. Blue PETG (Grover parts).

part = "body";        // "body" | "arm" | "pad" | "all" (preview)

// ---- chassis (measured) ---------------------------------------------------
acr_z0    = 55;       // acrylic underside above the bench
row_y     = -6;       // front hole row behind the acrylic's front edge  <- MEASURE
hole_x    = [-32, -16, 16, 32];
m4        = 4.5;
track_y0  = -10;      // tracks' first ground contact
track_r   = 38;       // front sprocket wrap radius (track arc to keep clear of)
track_x   = [52.5, 82.5];   // track inner / outer edge (30 mm tracks, 165 outside)

// ---- TFMini (Benewake drawing, as tfmini-bracket.scad) ----------------------
tf_zc = 53;  tf_face_y = 42;  tf_depth = 16;  tf_len = 42;  tf_body_w = 33;  tf_h = 15;
tf_ear_cc = 36;  tf_ear_d = 2.35;

// ---- cliff sensors -----------------------------------------------------------
cliff_x     = 67.5;   // in front of each track's centreline (today's position)
cliff_y     = 55;     // 65 mm ahead of the track contact (today's position)
cliff_face_z = 11;    // TCRT5000 face above the bench (was ~6)       <- verify reads
skid_drop   = 3;      // skids reach this far below the TCRT face
tcrt_l = 10.2;  tcrt_w = 5.8;  tcrt_h = 7.0;    // TCRT5000 body
pcb_l = 31.5;  pcb_w = 14;  pcb_t = 1.6;  pcb_hole_in = 7.5;   // HW-870

// ---- bumper ----------------------------------------------------------------
bump_y = 66;  bump_t = 6;  bump_z = [16, 26];  bump_x = 78;

// ---- servo arms (SG90) -------------------------------------------------------
sg_l = 22.5;  sg_w = 12.2;  sg_h = 22.7;  sg_tab_l = 32.2;  sg_tab_cc = 27.5;  sg_shaft_in = 5.9;
arm_x    = 45;        // pads over the rollers, 90 mm c-c
pivot_y  = 62;  pivot_z = 36;
roller_y = bump_y + bump_t + 50;    // bumper at the dock tip, rollers 50 mm on
roller_z = 13;        // pressed roller top (~9 base + 7 proud - 3 press)
arm_down = atan2(roller_z + 4 - pivot_z, roller_y - pivot_y);   // pad pivot 4 mm above its face
arm_len  = norm([roller_y - pivot_y, roller_z + 4 - pivot_z]);
arm_up   = 70;        // folded, degrees above horizontal
pad_x = 26;  pad_y = 24;  pad_t = 4;  run_dx = 8;  wire_d = 2.05;

$fn = 40;

module rbox(x0, y0, z0, x1, y1, z1, r = 1.5) {
  translate([x0, y0, z0]) cube([x1 - x0, y1 - y0, z1 - z0]);
}

module foot() {
  difference() {
    union() {
      rbox(-40, row_y - 14, acr_z0 - 6, 40, 6, acr_z0);          // under the acrylic
      rbox(-40, -0.01, acr_z0, 40, 3, acr_z0 + 2);                 // lip in front of the acrylic's edge
    }
    for (x = hole_x) translate([x, row_y, acr_z0 - 7]) cylinder(d = m4, h = 10);
    for (x = hole_x) translate([x, row_y, acr_z0 - 7]) cylinder(d = 8.6, h = 3.4, $fn = 6);  // nut pockets
  }
}

module tfmini_mount() {
  y0 = tf_face_y - tf_depth;          // the ears bolt to this plate's front face
  difference() {
    rbox(-tf_len / 2 - 3, y0 - 4, tf_zc - tf_h / 2 - 3, tf_len / 2 + 3, y0, acr_z0 - 6);
    for (s = [-1, 1]) translate([s * tf_ear_cc / 2, y0 - 5, tf_zc]) rotate([-90, 0, 0]) cylinder(d = tf_ear_d, h = 6);
    translate([-tf_body_w / 2 + 4, y0 - 5, tf_zc - tf_h / 2 + 3]) cube([tf_body_w - 8, 6, tf_h - 6]);   // cable window
  }
  // cheeks from the foot down to the plate
  for (s = [-1, 1]) rbox(s > 0 ? tf_len / 2 - 1 : -tf_len / 2 - 3, 0, tf_zc - tf_h / 2 - 3, s > 0 ? tf_len / 2 + 3 : -tf_len / 2 + 1, y0, acr_z0 - 6);
}

// crossbeam under the TFMini carrying the wings and the servos
module crossbeam() {
  rbox(-cliff_x - 8, 34, 18, cliff_x + 8, 48, 26);
  // ties from the crossbeam up to the TFMini cheeks / foot
  for (s = [-1, 1]) rbox(s > 0 ? 20 : -26, 6, 18, s > 0 ? 26 : -20, 48, acr_z0 - 6);
}

module cliff_wing(s) {
  x = s * cliff_x;
  difference() {
    union() {
      // board plate (HW-870 vertical, TCRT5000 end down, components facing back)
      rbox(x - pcb_w / 2 - 3, cliff_y + tcrt_w / 2 + 1, cliff_face_z + tcrt_h, x + pcb_w / 2 + 3, cliff_y + tcrt_w / 2 + 4, 48);
      // TCRT5000 socket: body pocket, open at the bottom for the beam
      rbox(x - tcrt_l / 2 - 1.6, cliff_y - tcrt_w / 2 - 1.6, cliff_face_z, x + tcrt_l / 2 + 1.6, cliff_y + tcrt_w / 2 + 1.6, cliff_face_z + tcrt_h + 2);
      // skids either side, sloped leading edge
      for (sx = [-1, 1]) hull() {
        rbox(x + sx * (tcrt_l / 2 + 2.5) - 1.2, cliff_y - 8, cliff_face_z - skid_drop + 2, x + sx * (tcrt_l / 2 + 2.5) + 1.2, cliff_y + 4, cliff_face_z + tcrt_h);
        rbox(x + sx * (tcrt_l / 2 + 2.5) - 1.2, cliff_y - 4, cliff_face_z - skid_drop, x + sx * (tcrt_l / 2 + 2.5) + 1.2, cliff_y + 2, cliff_face_z - skid_drop + 1);
      }
      // strut from the socket back up to the crossbeam
      rbox(x - 4, 40, 18, x + 4, cliff_y + tcrt_w / 2 + 4, 26);
    }
    rbox(x - tcrt_l / 2 - 0.2, cliff_y - tcrt_w / 2 - 0.2, cliff_face_z - 1, x + tcrt_l / 2 + 0.2, cliff_y + tcrt_w / 2 + 0.2, cliff_face_z + tcrt_h + 0.1);
    // lead slot up to the board
    rbox(x - 3.5, cliff_y - 1.5, cliff_face_z + tcrt_h - 1, x + 3.5, cliff_y + tcrt_w / 2 + 5, cliff_face_z + tcrt_h + 4);
    // board screw (M3), 7.5 mm from the pin end (top)
    translate([x, cliff_y, cliff_face_z + tcrt_h + 3 + pcb_l - pcb_hole_in]) rotate([-90, 0, 0]) cylinder(d = 3.2, h = 20);
  }
}

module bumper() {
  rbox(-bump_x, bump_y, bump_z[0], bump_x, bump_y + bump_t, bump_z[1]);
  for (s = [-1, 1]) rbox(s * cliff_x - 4, 48, bump_z[0], s * cliff_x + 4, bump_y, bump_z[1]);   // ties
}

// SG90 on its side, output shaft pointing OUTBOARD (+x on the right) at the pivot;
// modelled for the RIGHT side, mirrored for the left. Body rests on a floor over the
// bumper, its mounting tabs screw to a cradle plate.
sg_tab_from_base = 15.9;    // tab underside above the body's base (shaft end is the top)
module servo_mount_r() {
  bx1 = arm_x + 2;  bx0 = bx1 - sg_h;               // body along x, shaft face at bx1
  by0 = pivot_y - sg_shaft_in;  by1 = by0 + sg_l;  byc = (by0 + by1) / 2;
  tx = bx0 + sg_tab_from_base;                       // tab underside
  difference() {
    union() {
      rbox(bx0, 48, 18, tx, by1, pivot_z - sg_w / 2);                                        // floor
      rbox(tx - 2.5, byc - sg_tab_l / 2 - 2, 18, tx, byc + sg_tab_l / 2 + 2, pivot_z + sg_w / 2 + 2);   // cradle plate
    }
    rbox(tx - 3, by0 - 0.3, pivot_z - sg_w / 2 - 0.3, tx + 1, by1 + 0.3, pivot_z + sg_w / 2 + 0.3);    // body window
    for (dy = [-sg_tab_cc / 2, sg_tab_cc / 2])
      translate([tx - 4, byc + dy, pivot_z]) rotate([0, 90, 0]) cylinder(d = 2.2, h = 6);
  }
}
module servo_mount(s) { if (s > 0) servo_mount_r(); else mirror([1, 0, 0]) servo_mount_r(); }

module body() {
  foot(); tfmini_mount(); crossbeam(); bumper();
  for (s = [-1, 1]) { cliff_wing(s); servo_mount(s); }
}

// one arm (print 2, mirror one): servo-horn hub at the pivot, beam to the pad hinge
module arm(ang = arm_down) {
  translate([arm_x, pivot_y, pivot_z]) rotate([ang, 0, 0]) {
    rotate([0, 90, 0]) difference() { cylinder(d = 14, h = 4); translate([0, 0, -1]) cylinder(d = 2.2, h = 6); }
    rbox(0, 0, -3, 4, arm_len, 3);
    translate([0, arm_len, 0]) rotate([0, 90, 0]) difference() { cylinder(d = 8, h = 4); translate([0, 0, -1]) cylinder(d = 3.2, h = 6); }
  }
}

// pad: hangs on the arm tip's M3 hinge, copper runs fore-aft on the underside
module pad() {
  difference() {
    rbox(arm_x + 2 - pad_x / 2, roller_y - pad_y / 2, roller_z, arm_x + 2 + pad_x / 2, roller_y + pad_y / 2, roller_z + pad_t);
    for (dx = [-run_dx, 0, run_dx]) translate([arm_x + 2 + dx - 1.25, roller_y - pad_y / 2 + 2, roller_z - 0.01]) cube([2.5, pad_y - 4, 1.0]);
  }
}

module ghosts() {
  %translate([-60, -40, acr_z0]) cube([120, 40, 2]);                                 // acrylic (front strip)
  %translate([-tf_body_w / 2, tf_face_y - tf_depth, tf_zc - tf_h / 2]) cube([tf_body_w, tf_depth, tf_h]);   // TFMini
  for (s = [-1, 1]) %translate([s * 67.5 - 15, track_y0 - 60, 0]) cube([30, 60 + track_r, 76]);              // tracks (box)
  for (s = [-1, 1]) %translate([s * arm_x - 2.5, roller_y - 9.5, roller_z - 10]) cube([5, 19, 10]);           // rollers
  %translate([-82.5, bump_y + bump_t, 0]) cube([165, 50 + 20, 6]);                                           // dock base front
}

if (part == "body") body();
if (part == "arm") arm();
if (part == "pad") pad();
if (part == "all") {
  body();
  for (s = [-1, 1]) mirror([s < 0 ? 1 : 0, 0, 0]) { arm(); arm(arm_up); pad(); }
  ghosts();
}

echo(str("nose module: arm ", round(arm_len), " mm at ", round(arm_down), " deg down (folded ", arm_up,
         " up); rollers at y=", roller_y, "; cliff face ", cliff_face_z, " mm, skids ", cliff_face_z - skid_drop, " mm"));
