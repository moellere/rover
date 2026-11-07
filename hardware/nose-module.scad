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
// Front hole row: nearest hole edge 2 mm behind the acrylic's edge (Enoch, 11-07).
//
// Render: openscad -o nose-module.stl nose-module.scad
// Print:  part="print_body" (upside down: the lip and the TFMini plate top on the bed, tree
//         supports for the frame), part="print_arms" (flat, horn pocket down, one mirrored),
//         part="print_pads" (copper face down). Views: nose-module-print.png.

part = "body";        // "body" | "arm" | "pad" | "all" (preview)

// ---- chassis (measured) ---------------------------------------------------
acr_z0    = 55;       // acrylic underside above the bench
row_y     = -4.1;     // front hole row centres behind the acrylic's edge (Enoch 11-07: hole edge 2 mm in, 4.2 holes)
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
tcrt_l = 10.2;  tcrt_w = 5.8;  tcrt_h = 7.0;    // TCRT5000 body; on the HW-870 its LONG axis runs across the
                                                 // board's width (Enoch's photo, 11-07) = fore-aft on Grover
skid_off    = tcrt_w / 2 + 1.6 + 3.5 + 1.2;   // skid centre from the TCRT centre (3.5 mm clear of the socket)
pcb_l = 31.5;  pcb_w = 14;  pcb_t = 1.6;  pcb_hole_in = 7.5;   // HW-870 (Enoch, 10-03)
// Board FLAT, as on today's cliff mounts (v4): sensor side down, lying ACROSS Grover,
// TCRT5000 at the outboard end over the track, pins pointing inboard; component side up
// against a boss under a shelf (M3 + nut).
tcrt_in  = 4;         // TCRT5000 centre from the board's sensor-end edge
tcrt_gap = 0;         // TCRT body to board (0 = seated on the board; raise if its leads stay long)
boss_h   = 6;         // clears the pot and solder tails
pcb_z0   = cliff_face_z + tcrt_h + tcrt_gap;       // board underside
shelf_z0 = pcb_z0 + pcb_t + boss_h;                // shelf underside
shelf_t  = 4;
pcb_x1   = cliff_x + tcrt_in;  pcb_x0 = pcb_x1 - pcb_l;   // outboard / inboard (pin) ends

// ---- bumper ----------------------------------------------------------------
bump_y = 66;  bump_t = 6;  bump_z = [16, 26];  bump_x = 78;

// ---- servo arms (SG90; Enoch's are Smraza S51 9 g, same body) -------------------------------------------------------
// Datasheet Enoch matched to the S51 (11-07): B 23 long, D 12 thick, E 32 over the tabs,
// F 19.5 base to tab top, C 28.5 base to gear-housing top, A 32 base to spline top.
sg_l = 23;  sg_w = 12.2;  sg_h = 22.7;  sg_tab_l = 32.2;  sg_tab_cc = 27.5;  sg_shaft_in = 5.9;
arm_x    = 45;        // pads over the rollers, 90 mm c-c
pivot_y  = 64;  pivot_z = 36;   // gear housing clears the cliff board's screw
roller_y = bump_y + bump_t + 50;    // bumper at the dock tip, rollers 50 mm on
roller_z = 13;        // pressed roller top (~9 base + 7 proud - 3 press)
hinge_h  = 9;         // pad hinge axis above the pad face (pad 4 + clearance for the arm's tip boss)
arm_down = atan2(roller_z + hinge_h - pivot_z, roller_y - pivot_y);
arm_len  = norm([roller_y - pivot_y, roller_z + hinge_h - pivot_z]);
sg_spline = 7.0;      // case top to the underside of the horn arm (Enoch measured, 11-07)
horn_x   = arm_x + 6.3;  // the arm's inner face sits on the horn here (fixed: clear of the cliff board plate at 60.5)
sg_top_x = horn_x - sg_spline; // servo case top (shaft end)
arm_t    = 4;         // arm thickness (x)
// SG90 single-arm horn (the one in the bag) sits in a pocket on the arm's inner face  <- check yours
horn_hub_d = 7.4;  horn_len = 17;  horn_w0 = 5.6;  horn_w1 = 4.0;  horn_t = 1.6;  horn_holes = [10, 14];
leaf_t   = 2.2;       // flexure: thinned arm section, gives the pad a few mm of spring
leaf_at  = [26, 44];  // along the arm from the pivot
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

// The lead leaves the TFMini's TOP face (Enoch, 11-07), so the plate stops below
// the top and leaves the connector free; the ears bolt to its front face.
module tfmini_mount() {
  y0 = tf_face_y - tf_depth;
  difference() {
    rbox(-tf_len / 2 - 3, y0 - 4, tf_zc - tf_h / 2 - 3, tf_len / 2 + 3, y0, acr_z0 + 2);   // top level with the lip: both sit on the bed
    for (s = [-1, 1]) translate([s * tf_ear_cc / 2, y0 - 5, tf_zc]) rotate([-90, 0, 0]) cylinder(d = tf_ear_d, h = 6);
  }
  // cheeks from the foot down to the plate
  for (s = [-1, 1]) rbox(s > 0 ? tf_len / 2 - 1 : -tf_len / 2 - 3, 0, tf_zc - tf_h / 2 - 3, s > 0 ? tf_len / 2 + 3 : -tf_len / 2 + 1, y0, acr_z0 - 6);
}

// crossbeam under the TFMini carrying the wings and the servos
module crossbeam() {
  rbox(-cliff_x - 8, 34, 18, cliff_x + 8, 46, 26);
  // ties from the crossbeam up to the TFMini cheeks / foot
  for (s = [-1, 1]) rbox(s > 0 ? 20 : -26, 6, 18, s > 0 ? 26 : -20, 46, acr_z0 - 6);
}

// Wing, RIGHT side (mirrored for the left): a shelf over the board (which also carries the
// servo), an end wall outboard of the board down to the TCRT socket and skids.
module cliff_wing_r() {
  x = cliff_x;  y0 = cliff_y - pcb_w / 2 - 1;  y1 = cliff_y + pcb_w / 2 + 1;
  difference() {
    union() {
      rbox(20, y0, shelf_z0, pcb_x1 + 4, y1, shelf_z0 + shelf_t);                        // shelf
      rbox(pcb_x1 + 0.5, 34, cliff_face_z, pcb_x1 + 4, y1, shelf_z0 + shelf_t);          // end wall, back to the crossbeam
      translate([pcb_x0 + pcb_hole_in, cliff_y, pcb_z0 + pcb_t]) cylinder(d = 8, h = boss_h + 0.1);   // boss
      for (sy = [-1, 1])                                                                 // ribs either side of the board
        rbox(pcb_x0 + pcb_hole_in + 6, cliff_y + sy * (pcb_w / 2 + 0.3) + (sy > 0 ? 0 : -1.6), pcb_z0 - 0.5,
             pcb_x1 + 1, cliff_y + sy * (pcb_w / 2 + 0.3) + (sy > 0 ? 1.6 : 0), shelf_z0);
      // TCRT5000 socket under the board's outboard end, tied to the end wall
      rbox(x - tcrt_w / 2 - 1.6, cliff_y - tcrt_l / 2 - 1.6, cliff_face_z, pcb_x1 + 1, cliff_y + tcrt_l / 2 + 1.6, pcb_z0 - 0.2);
      // skids either side, 3.5 mm clear of the socket so they stay out of the beam, with
      // the slope on the LEADING (+y) edge; a bridge under the board joins them to the socket
      for (sx = [-1, 1]) hull() {
        rbox(x + sx * skid_off - 1.2, cliff_y - 4, cliff_face_z - skid_drop + 2, x + sx * skid_off + 1.2, cliff_y + 8, pcb_z0 - 1);
        rbox(x + sx * skid_off - 1.2, cliff_y - 2, cliff_face_z - skid_drop, x + sx * skid_off + 1.2, cliff_y + 4, cliff_face_z - skid_drop + 1);
      }
      rbox(x - skid_off - 1.2, cliff_y - 4, pcb_z0 - 3, x + skid_off + 1.2, cliff_y + 4, pcb_z0 - 1);   // bridge (1 mm under the board)
      rbox(pcb_x1 - 8, y1 - 0.01, bump_z[0], pcb_x1 + 4, bump_y + 0.01, shelf_z0 + shelf_t);   // tie down to the bumper
    }
    rbox(x - tcrt_w / 2 - 0.2, cliff_y - tcrt_l / 2 - 0.2, cliff_face_z - 1, x + tcrt_w / 2 + 0.2, cliff_y + tcrt_l / 2 + 0.2, pcb_z0 + 0.1);
    translate([pcb_x0 + pcb_hole_in, cliff_y, pcb_z0 - 1]) cylinder(d = 3.2, h = 20);                   // M3
    translate([pcb_x0 + pcb_hole_in, cliff_y, shelf_z0 + shelf_t - 2.6]) cylinder(d = 6.4, h = 3, $fn = 6);   // nut, top
  }
}
module cliff_wing(s) { if (s > 0) cliff_wing_r(); else mirror([1, 0, 0]) cliff_wing_r(); }

module bumper() {
  rbox(-bump_x, bump_y, bump_z[0], bump_x, bump_y + bump_t, bump_z[1]);   // tied up to the wings and the servo floors
}

// SG90 on its side, output shaft pointing OUTBOARD (+x on the right) at the pivot;
// modelled for the RIGHT side, mirrored for the left. Body rests on a floor over the
// bumper, its mounting tabs screw to a cradle plate.
sg_tab_from_base = 19.5 - 2.5;   // tab underside above the base (F 19.5 to the tab top, tab 2.5 thick)
module servo_mount_r() {
  bx1 = sg_top_x;  bx0 = bx1 - sg_h;                // body along x, shaft end at bx1
  by0 = pivot_y - sg_shaft_in;  by1 = by0 + sg_l;  byc = (by0 + by1) / 2;
  tx = bx0 + sg_tab_from_base;                       // tab underside
  difference() {
    union() {
      rbox(bx0, cliff_y - pcb_w / 2 - 1, shelf_z0, tx, by1, pivot_z - sg_w / 2);           // floor, on the shelf and the bumper
      rbox(bx0, bump_y, bump_z[0], tx, bump_y + bump_t, shelf_z0 + 0.1);
      rbox(tx - 2.5, byc - sg_tab_l / 2 - 2, shelf_z0, tx, byc + sg_tab_l / 2 + 2, pivot_z + sg_w / 2 + 2);   // cradle plate (above the board's connector)
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

// one arm (RIGHT shown; print one as modelled and one mirrored): horn pocket at the
// pivot, a thin leaf section as the spring, M3 hinge boss at the tip for the pad.
module arm(ang = arm_down) {
  translate([horn_x, pivot_y, pivot_z]) rotate([ang, 0, 0]) difference() {
    union() {
      rotate([0, 90, 0]) cylinder(d = 14, h = arm_t);
      rbox(0, 0, -3, arm_t, leaf_at[0], 3);
      rbox(0, leaf_at[0], -leaf_t / 2, arm_t + 2, leaf_at[1], leaf_t / 2);      // leaf: 6 wide, 2.2 thick
      rbox(0, leaf_at[1], -3, arm_t, arm_len, 3);
      translate([0, arm_len, 0]) rotate([0, 90, 0]) cylinder(d = 8, h = arm_t);
    }
    // horn pocket on the inner face (x = 0), horn pointing along the arm
    translate([-0.01, 0, 0]) rotate([0, 90, 0]) cylinder(d = horn_hub_d + 0.4, h = horn_t + 0.2);
    translate([-0.01, 0, 0]) rotate([0, 90, 0]) linear_extrude(horn_t + 0.2)
      polygon([[horn_w0 / 2 + 0.2, 0], [horn_w1 / 2 + 0.2, horn_len], [-horn_w1 / 2 - 0.2, horn_len], [-horn_w0 / 2 - 0.2, 0]]);
    translate([-1, 0, 0]) rotate([0, 90, 0]) cylinder(d = 2.4, h = arm_t + 2);                  // horn screw
    for (h = horn_holes) translate([-1, h, 0]) rotate([0, 90, 0]) cylinder(d = 1.6, h = arm_t + 2);   // M2 self-tappers
    translate([-1, arm_len, 0]) rotate([0, 90, 0]) cylinder(d = 3.2, h = arm_t + 2);            // hinge pin
  }
}

// pad: two lugs straddle the arm's tip boss on an M3 pin, so the pad pitches to sit
// flat on the roller; three fore-aft copper runs underneath, all one 12 AWG wire laced
// through end holes and soldered to the lead at the rear.
pad_cx = arm_x;       // pad centred over the roller
module pad() {
  hz = roller_z + hinge_h;  hy = roller_y;  lx = horn_x + arm_t / 2;
  difference() {
    union() {
      rbox(pad_cx - pad_x / 2, roller_y - pad_y / 2, roller_z, pad_cx + pad_x / 2, roller_y + pad_y / 2, roller_z + pad_t);
      for (sx = [-1, 1]) hull() {
        translate([lx + sx * (arm_t / 2 + 1.75) - 1.5, hy, hz]) rotate([0, 90, 0]) cylinder(d = 8, h = 3);
        rbox(lx + sx * (arm_t / 2 + 1.75) - 1.5, hy - 5, roller_z + pad_t - 0.1, lx + sx * (arm_t / 2 + 1.75) + 1.5, hy + 5, roller_z + pad_t);
      }
    }
    translate([lx - 8, hy, hz]) rotate([0, 90, 0]) cylinder(d = 3.2, h = 16);
    for (dx = [-run_dx, 0, run_dx]) {
      translate([pad_cx + dx - 1.15, roller_y - pad_y / 2 + 2, roller_z - 0.01]) cube([2.3, pad_y - 4, 1.0]);   // groove, wire 1 mm proud
      for (dy = [-1, 1]) translate([pad_cx + dx, roller_y + dy * (pad_y / 2 - 2), roller_z - 1]) cylinder(d = 2.5, h = pad_t + 2);
    }
    for (dx = [-run_dx / 2, run_dx / 2]) {      // top-side lacing grooves between runs
      dy = dx < 0 ? 1 : -1;
      translate([pad_cx + dx - run_dx / 2, roller_y + dy * (pad_y / 2 - 2) - 1.15, roller_z + pad_t - 1]) cube([run_dx, 2.3, 1.1]);
    }
  }
}

// ---- reference parts for the assembly drawing (not printed) ----------------------
module tfmini_dummy() {
  translate([-tf_body_w / 2, tf_face_y - tf_depth, tf_zc - tf_h / 2]) cube([tf_body_w, tf_depth, tf_h]);
  translate([-tf_len / 2, tf_face_y - tf_depth, tf_zc - 3]) cube([tf_len, 2, 6]);
}
module cliff_dummy(s) {
  x = s * cliff_x;
  translate([x - tcrt_w / 2, cliff_y - tcrt_l / 2, cliff_face_z]) cube([tcrt_w, tcrt_l, tcrt_h]);                 // TCRT5000
  translate([s > 0 ? pcb_x0 : -pcb_x1, cliff_y - pcb_w / 2, pcb_z0]) cube([pcb_l, pcb_w, pcb_t]);   // HW-870, flat
  translate([s > 0 ? pcb_x0 - 8 : -pcb_x0, cliff_y - 5, pcb_z0 + pcb_t]) cube([8, 10, 2.5]);         // header + plug, inboard
}
module servo_dummy_r() {
  bx1 = sg_top_x;  bx0 = bx1 - sg_h;  by0 = pivot_y - sg_shaft_in;
  translate([bx0, by0, pivot_z - sg_w / 2]) cube([sg_h, sg_l, sg_w]);
  translate([bx0 + sg_tab_from_base, by0 - (sg_tab_l - sg_l) / 2, pivot_z - sg_w / 2]) cube([2.5, sg_tab_l, sg_w]);
  translate([bx1, pivot_y, pivot_z]) rotate([0, 90, 0]) cylinder(d = 11.8, h = 28.5 - sg_h);
  translate([bx1, pivot_y, pivot_z]) rotate([0, 90, 0]) cylinder(d = 4.8, h = 32 - sg_h);
}
module servo_dummy(s) { if (s > 0) servo_dummy_r(); else mirror([1, 0, 0]) servo_dummy_r(); }

// wires: polyline of points, drawn as a chain of hulled spheres
module wire(pts, d = 1.6) { for (i = [0 : len(pts) - 2]) hull() { translate(pts[i]) sphere(d = d, $fn = 8); translate(pts[i + 1]) sphere(d = d, $fn = 8); } }
deck_z = 95;          // where leads leave the drawing, up toward the spine deck
module wires_tfmini() {   // connector on the top face, toward the rear (position along the top not measured)
  zt = tf_zc + tf_h / 2;  yc = tf_face_y - tf_depth + 4;
  wire([[0, yc, zt], [0, yc, zt + 6], [0, 6, zt + 6], [0, -10, deck_z]], 3.0);
}
module wires_cliff(s) {
  xp = s * (pcb_x0 - 8);  zp = pcb_z0 + pcb_t + 1.2;   // out of the plug, inboard, then back under the shelf
  for (i = [-1, 0, 1]) wire([[xp, cliff_y + i * 2.54, zp], [s * 30, cliff_y + i * 2.54, zp], [s * 30, 47, zp + i * 1.5], [s * (28 + i * 1.6), 30, 30], [s * (34 + i * 1.6), -10, deck_z]]);
}
module wires_servo(s) {   // lead leaves the SHAFT-end face (rear here), near the base (Enoch + S51 photo, 11-07)
  bx0 = sg_top_x - sg_h;  yl = pivot_y - sg_shaft_in;
  for (i = [-1, 0, 1]) wire([[s * (bx0 + 3), yl, pivot_z + i * 1.3], [s * (bx0 + 3), yl - 3, pivot_z + i * 1.3], [s * (bx0 + 3), 50, 32 + i * 1.3], [s * (30 + i * 1.3), 30, 30], [s * (30 + i * 1.3), 4, 50], [s * (30 + i * 1.3), -10, deck_z]], 1.3);
}
module wires_pad(s, ang) {  // pad lead: along the arm, a loop round the pivot, then back to the deck
  hz = roller_z + hinge_h;  lx = horn_x + arm_t + 1.5;
  tip = [lx, pivot_y + arm_len * cos(ang), pivot_z + arm_len * sin(ang)];
  mid = [lx, pivot_y + 30 * cos(ang), pivot_z + 30 * sin(ang)];
  pts = [[pad_cx, roller_y - pad_y / 2 + 2, roller_z + pad_t], [lx, roller_y - 4, roller_z + pad_t + 2], tip, mid,
         [lx, pivot_y, pivot_z + 10], [lx, pivot_y - 10, pivot_z + 4], [lx, 50, 40], [s > 0 ? 50 : 50, 20, 52], [50, -10, deck_z]];
  if (s > 0) wire(pts, 2.6); else mirror([1, 0, 0]) wire(pts, 2.6);
}

module ghosts() {
  %translate([-60, -40, acr_z0]) cube([120, 40, 2]);                                 // acrylic (front strip)
  %tfmini_dummy();
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
// assembly drawing: one STL per item, coloured by scripts/nose_assembly_views.py
if (part == "asm_arms")   for (s = [-1, 1]) mirror([s < 0 ? 1 : 0, 0, 0]) { arm(); pad(); }
if (part == "asm_tfmini") tfmini_dummy();
if (part == "asm_cliff")  for (s = [-1, 1]) cliff_dummy(s);
if (part == "asm_servo")  for (s = [-1, 1]) servo_dummy(s);
if (part == "asm_w_tfmini") wires_tfmini();
if (part == "asm_w_cliff")  for (s = [-1, 1]) wires_cliff(s);
if (part == "asm_w_servo")  for (s = [-1, 1]) wires_servo(s);
if (part == "asm_w_pad")    for (s = [-1, 1]) wires_pad(s, arm_down);

echo(str("nose module: arm ", round(arm_len), " mm at ", round(arm_down), " deg down (folded ", arm_up,
         " up); rollers at y=", roller_y, "; cliff face ", cliff_face_z, " mm, skids ", cliff_face_z - skid_drop, " mm"));

// ---- print layouts (2026-11-07): body upside down, acrylic face toward the bed (lip and
// TFMini plate top touch it; tree supports under the foot's 2 mm step); arms flat on
// their horn face, one mirrored; pads face down (lugs up).
if (part == "print_body") translate([0, 0, acr_z0 + 2]) rotate([0, 180, 0]) body();   // a ROTATION, not a mirror
if (part == "print_arms") for (s = [-1, 1]) translate([s * 12, 0, 0]) mirror([s < 0 ? 1 : 0, 0, 0])
  translate([0, 0, 0]) rotate([0, -90, 0]) translate([-horn_x, -pivot_y, -pivot_z]) arm(0);
if (part == "print_pads") for (s = [-1, 1]) translate([s * 20, 0, 0]) mirror([s < 0 ? 1 : 0, 0, 0])
  translate([-pad_cx, -roller_y, -roller_z]) pad();

// ---- context for the drawing: Grover's front end and the dock (APPROXIMATE) ------------
// Measured: acrylic underside 55 / ~2 thick, its front edge 10 mm ahead of the tracks'
// first ground contact, tracks 30 wide and 165 over the outside. Guessed: the track's
// front profile (ground run to y -10, rising to an idler, front ~y 30), beam sizes, the
// acrylic's width and the spine deck. Dock: base tip at the bumper face, rollers 50 mm on.
module ctx_grover() {
  for (s = [-1, 1]) {
    hull() {                                                     // track (front 140 mm)
      translate([s * 67.5 - 15, -10, 18]) rotate([0, 90, 0]) cylinder(r = 18, h = 30);
      translate([s * 67.5 - 15, 12, 40]) rotate([0, 90, 0]) cylinder(r = 18, h = 30);
      translate([s * 67.5 - 15, -150, 18]) rotate([0, 90, 0]) cylinder(r = 18, h = 30);
      translate([s * 67.5 - 15, -150, 40]) rotate([0, 90, 0]) cylinder(r = 18, h = 30);
    }
    translate([s * 47 - 4, -150, 40]) cube([8, 160, 24]);       // tread beam (Makeblock, approx.)
    for (y = [-30, -120]) translate([s * 40, y, acr_z0 + 2]) cylinder(d = 5, h = 30);   // deck posts
  }
  translate([-55, -150, acr_z0]) cube([110, 150, 2]);           // acrylic plate
  translate([-50, -130, acr_z0 + 32]) cube([100, 110, 4]);      // spine deck (approx.)
}
module ctx_dock() {
  y0 = bump_y + bump_t;
  hull() {                                                       // base: low tip rising to the roller deck
    translate([-82.5, y0, 0]) cube([165, 1, 6]);
    translate([-82.5, y0 + 35, 0]) cube([165, 60, 9]);
  }
  for (s = [-1, 1]) translate([s * arm_x - 2.5, roller_y, roller_z - 3]) rotate([0, 90, 0]) cylinder(d = 19, h = 5);   // rollers
}
if (part == "ctx_grover") ctx_grover();
if (part == "ctx_dock")   ctx_dock();
// as installed (frame as above: bench at z=0), for viewing: printed parts only, or with
// the TFMini, cliff boards and servos as plain blocks
if (part == "installed") { body(); for (s = [-1, 1]) mirror([s < 0 ? 1 : 0, 0, 0]) { arm(); pad(); } }
if (part == "installed_parts") { body(); for (s = [-1, 1]) { mirror([s < 0 ? 1 : 0, 0, 0]) { arm(); pad(); } cliff_dummy(s); servo_dummy(s); } tfmini_dummy(); }
