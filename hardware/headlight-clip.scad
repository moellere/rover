// Headlight clip: two WS2812B dots (BTF-Lighting, 10 mm dia, 3 mm thick,
// pads on the back) either side of the T-Camera, clipped around the camera
// mount's cradle (camera-mount.scad v7) so they tilt with the lens and light
// the dock marker for the onboard camera's final approach (2026-10-26).
//
// Shape: a C-band around the cradle from behind - a strap across the back
// plate, an arm down each side rail's outer face, and a small hook over the
// front edge of each rail (the rails only; nothing reaches over the board's
// face, so the OLED, buttons and lens stay clear). A pod on each arm holds a
// dot in a rear-loading pocket: the board drops in from behind against a
// front lip with a 7 mm window and is glued there (v3; a snap rim was too
// tight to print). Wires leave straight out the open back.
//
// Frame: camera-mount.scad's cradle_flat - board face +Z (forward when
// mounted), board length +Y, X across. Values below are copied from it.
//
// Render:  openscad -o headlight-clip.stl headlight-clip.scad
// Print:   band edge down (print_orient), no supports, no brim.

pcb_w = 28.0; pcb_t = 1.27; comp_back = 6.0; wall = 3.0; clear = 0.3; lip = 2.0;
inner_w = pcb_w + 2 * clear;
inner_t = pcb_t + 2 * clear;
outer_w = inner_w + 2 * wall;                 // cradle width, 34.6
z0      = -(comp_back + wall);                // back face of the back plate
z_front = z0 + comp_back + wall + inner_t + lip;   // rail front edge (z0 + depth)

fit    = 0.25;   // clearance around the cradle
t      = 2.0;    // band thickness
hook   = 1.6;    // how far each hook reaches in over the rail's front edge (rail is 3 mm)
hook_t = 1.5;

dot_d   = 10.0;  // measured (Enoch)
dot_t   = 3.0;   // board + LED
window  = 7.0;   // the 5050 LED is 5 mm square
lip_t   = 1.2;
pocket_clear = 2.0;   // pocket dia over dot_d. v1 +0.4 and v2 +1.4 (with a snap rim) were
                      // both too tight: the pockets print as horizontal holes, which come out
                      // small and sag at the top. v3: 12 mm, teardrop top, no snap rim - the
                      // dot is held against the front lip by a dab of glue (Enoch, 10-26).
dot_x   = 25;    // dot centre from the lens axis, each side (Enoch's spacing: 50 mm)
pod_w   = dot_d + pocket_clear + 3;   // v3: room around the teardrop pocket
band    = pod_w;  // band height along the cradle (Y); = pod_w so the pods sit on the bed

xo = outer_w / 2 + fit;          // inner face of each arm
zb = z0 - fit;                   // inner face of the strap
zf = z_front + fit;              // hooks' inner face

$fn = 48;

module band_part() {
  // strap behind the back plate
  translate([-xo - t, 0, zb - t]) cube([2 * (xo + t), band, t]);
  for (s = [-1, 1]) mirror([s < 0 ? 1 : 0, 0, 0]) {
    // arm along the rail's outer face
    translate([xo, 0, zb - t]) cube([t, band, zf - zb + t + hook_t]);
    // hook over the rail's front edge
    translate([xo - hook, 0, zf]) cube([hook + t, band, hook_t]);
  }
}

module pod() {
  zfront = zf + hook_t;                 // pod front flush with the hooks
  depth  = lip_t + dot_t + 1.0;         // lip + dot + snap rim
  difference() {
    hull() {
      translate([dot_x, band / 2, zfront - depth]) cylinder(d = pod_w, h = depth);
      translate([xo + t - 0.01, band / 2 - pod_w / 2, zfront - depth]) cube([0.01, pod_w, depth]);
    }
    // window through the front lip
    translate([dot_x, band / 2, zfront - lip_t - 0.01]) cylinder(d = window, h = lip_t + 0.02);
    // pocket for the board, behind the lip, open at the back. Teardrop toward +Y,
    // which is up when printed (print_orient), so the top of the hole prints true.
    translate([dot_x, band / 2, zfront - depth - 0.01]) hull() {
      cylinder(d = dot_d + pocket_clear, h = dot_t + 1.02);
      translate([0, (dot_d + pocket_clear) / 2 * 1.15, 0]) cylinder(d = 0.1, h = dot_t + 1.02);
    }
  }
}

module part() {
  band_part();
  for (s = [-1, 1]) mirror([s < 0 ? 1 : 0, 0, 0]) pod();
}

print_orient = true;
// band edge on the bed: the C-profile prints as a straight extrusion; the
// pockets are short horizontal holes (10 mm bridges fine in PETG)
if (print_orient) rotate([90, 0, 0]) part(); else part();
