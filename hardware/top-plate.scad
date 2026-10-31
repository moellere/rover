// Top plate: Grover's electronics deck, fixed on the four 30 mm posts
// (64 x 96 mm centres), sitting directly on them (2026-10-31). Replaces battery
// cradle v3 on the posts - the pack now rides in battery-tray.scad behind the
// acrylic - so nothing under this plate needs regular access: no hinge.
//
// Carries:
//   - the Freenove FNK0101 breakout (devkit fitted) on 5 mm standoffs at its
//     81 x 77 mm M3 holes - left side, power-jack edge to the REAR;
//   - the 400-point half breadboard (82 x 54 x 9, adhesive back) in a 1.5 mm
//     locating pocket - right side;
//   - the camera perch on a front tab, with cradle v3's M4 grid (8 mm pitch,
//     columns +/-24..0, rows 12 and 20 mm ahead of the front posts) and its
//     cable drop, so camera mount v7 bolts on exactly as before - ~7.5 mm lower
//     than on cradle v3 (11 mm thick there, 3.5 here);
//   - cable slots: between the two boards, and ahead of the FNK0101 for the
//     sensor leads coming up from the deck.
// No risers (Enoch, 10-31, with a photo of cradle v3 on the posts): the post
// tops stand well clear of the track tops, so the plate can be wider than the
// tracks' inside gap and still pass over them, and the driver tray and Wagos on
// the acrylic fit underneath. Width limit ~160 mm (tracks 165 mm outside).
// v1/v1b had 15 mm risers (job 5e2d54e100, skipped).
//
// Frame: +y FORWARD, +x Grover's RIGHT, z up (right-handed: forward x up =
// right - checked per CLAUDE.md's handedness rule). Origin: centre of the posts.
//
// Measured: posts 64 x 96 (battery-cradle.scad); FNK0101 87.6 x 83.2 mm, holes
// 3.4 mm at 81 x 77 (Freenove diagram, spacing calipered by Enoch 10-26), 20 mm
// tall with the devkit incl. the pins under the board (Enoch, 10-31); breadboard 82 x 54 x 9 (Enoch); camera grid from cradle v3.
//
// Render: openscad -o top-plate.stl top-plate.scad
// Print:  flat, standoffs up, no supports, no brim. Blue PETG (Grover parts).

plate_t  = 3.5;
corner_r = 4;
m4_hole  = 4.5;
m3_pilot = 2.6;

post_x = 32;  post_y = 48;            // posts at (+/-32, +/-48)
post_slot = 1.5;                       // +/- fore-aft; cradle v3 (which fitted these posts) had +/-1

// Freenove FNK0101 - devkit's long axis along y (its 83.2 side)
fn_w = 87.6;  fn_l = 83.2;  fn_hx = 81 / 2;  fn_hy = 77 / 2;
fn_stand_h = 5;  fn_stand_d = 7;
// breadboard
bb_w = 54;  bb_l = 82;  bb_fit = 0.6;  bb_recess = 1.5;

margin = 3;  gap = 8;                  // gap between the boards = cable slot
total_w = margin + fn_w + gap + bb_w + bb_fit + margin;    // ~157
x0 = -total_w / 2;
fn_cx = x0 + margin + fn_w / 2;
bb_cx = fn_cx + fn_w / 2 + gap + (bb_w + bb_fit) / 2;
gap_cx = fn_cx + fn_w / 2 + gap / 2;

body_y0 = -post_y - 5;                 // rear edge, covers the rear posts
body_y1 = 42;                          // front of the board area
fn_cy = (body_y0 + body_y1) / 2 + 1;
bb_cy = fn_cy + 3;                     // 3 mm forward: clears the right rear post's bolt head

// camera perch tab (cradle v3's front tab, in this frame)
tab_w = 80;
perch_y = post_y + 12;                 // grid centre row (cradle v3: 12 mm ahead of the front bolts)
perch_rows = [0, 8];                   // the second row 8 mm further forward
perch_cols = [-24, -16, -8, 0, 8, 16, 24];
tab_y1 = post_y + 38;                  // tab front edge, as cradle v3

$fn = 32;

module rrect(xa, ya, xb, yb, h) {
  linear_extrude(h) offset(r = corner_r) offset(delta = -corner_r) translate([xa, ya]) square([xb - xa, yb - ya]);
}

module plate() {
  difference() {
    union() {
      rrect(x0, body_y0, -x0, body_y1, plate_t);                         // board area
      rrect(-tab_w / 2, body_y1 - 10, tab_w / 2, tab_y1, plate_t);       // camera tab
      for (sx = [-1, 1], sy = [-1, 1])                                    // FNK0101 standoffs
        translate([fn_cx + sx * fn_hx, fn_cy + sy * fn_hy, 0]) cylinder(d = fn_stand_d, h = plate_t + fn_stand_h);
    }
    // post bolts, slotted fore-aft (cradle v3 had +/-1 mm and fitted these posts)
    for (sx = [-1, 1], sy = [-1, 1]) hull() for (dy = [-post_slot, post_slot])
      translate([sx * post_x, sy * post_y + dy, -1]) cylinder(d = m4_hole, h = plate_t + 2);
    // FNK0101 pilots
    for (sx = [-1, 1], sy = [-1, 1])
      translate([fn_cx + sx * fn_hx, fn_cy + sy * fn_hy, -1]) cylinder(d = m3_pilot, h = plate_t + fn_stand_h + 2);
    // breadboard locating pocket
    translate([bb_cx - (bb_w + bb_fit) / 2, bb_cy - (bb_l + bb_fit) / 2, plate_t - bb_recess]) cube([bb_w + bb_fit, bb_l + bb_fit, bb_recess + 1]);
    // camera perch grid and cable drop (as cradle v3)
    for (x = perch_cols, dy = perch_rows) translate([x, perch_y + dy, -1]) cylinder(d = m4_hole, h = plate_t + 2);
    hull() for (y = [perch_y - 3 - 1.5, perch_y - 3 + 1.5]) translate([0, y, -1]) cylinder(d = 13, h = plate_t + 2);
    // cable slots: between the boards, and the front corners of the board area
    translate([gap_cx - 2.5, fn_cy - 30, -1]) cube([5, 60, plate_t + 2]);
    // left front slot, in the strip ahead of the FNK0101 (the breadboard reaches the front on the right)
    translate([fn_cx - 15, fn_cy + fn_l / 2 + 0.8, -1]) cube([30, body_y1 - (fn_cy + fn_l / 2) - 2.3, plate_t + 2]);
  }
}

module ghosts() {
  %translate([fn_cx - fn_w / 2, fn_cy - fn_l / 2, plate_t + fn_stand_h]) cube([fn_w, fn_l, 20]);
  %translate([bb_cx - bb_w / 2, bb_cy - bb_l / 2, plate_t - bb_recess]) cube([bb_w, bb_l, 9]);
  %translate([-30, perch_y - 18, plate_t]) cube([60, 44, 4]);   // camera mount base
}

plate(); ghosts();
