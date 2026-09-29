// Camera adapter strip: bolts the v5 camera cradle (camera-mount.scad) rigidly
// to the rover chassis. The cradle used to sit loose on the plate and shifted
// on every jerky pulse, which corrupted the marker bearings.
//
// The strip spans the two front M4 standoffs on the chassis plate (Makeblock
// grid, 64 mm centre-to-centre, 30 mm tall) and bolts down into their tops.
// On top it presents the cradle's own hole pattern (M4 slots on 8 mm
// centres) so the cradle bolts to the strip with two M4 screws and nuts.
// The camera lead drops through a narrow slot under the cradle - plug the
// camera in and seat it in the cradle first, then bolt the cradle down.
//
// Orientation: the strip runs LEFT-RIGHT across the rover (X); Y is the
// travel axis, +Y forward. Print flat, no supports, no brim.
//
// Render:  openscad -o camera-strip.stl camera-strip.scad

// ---- Chassis (measured by Enoch, 2026-09-29) --------------------------------
post_cc     = 64.0;   // standoff centre-to-centre; measured 68.5 mm across the
                      // outer edges of the M4 holes, i.e. 8 Makeblock grid units
post_slot_l = 6.5;    // slot length along X so 63-66 mm c-c all fit
m4_hole     = 4.5;    // M4 clearance, slightly oversized on purpose (Enoch's ask)

// ---- Cradle interface (must match camera-mount.scad) -----------------------
mb_pitch    = 8;      // cradle slots sit at x = +/-8
cradle_slot = 8;      // cradle slot length along Y - mirrored here for +/-4 mm adjust
cable_w     = 8.0;    // cable-only pass-through (the plug goes in before bolting)
cable_l     = 18.0;
cable_y     = 3.0;    // same aft offset as the cradle's cable slot

// ---- Strip ------------------------------------------------------------------
strip_l = post_cc + 20;   // 84 mm: 10 mm of material beyond each post
strip_w = 34;
strip_t = 4;
corner  = 4;

$fn = 48;

module slot(len, d, along = "y") {
  a = (along == "x") ? [1, 0] : [0, 1];
  hull() for (s = [-1, 1]) translate([s * a[0] * (len - d) / 2, s * a[1] * (len - d) / 2, -1])
    cylinder(d = d, h = strip_t + 2);
}

module strip() {
  difference() {
    linear_extrude(strip_t)
      offset(r = corner) offset(delta = -corner) square([strip_l, strip_w], center = true);
    // standoff bolts, slotted along X to absorb the c-c uncertainty
    for (x = [-post_cc / 2, post_cc / 2]) translate([x, 0, 0]) slot(post_slot_l, m4_hole, "x");
    // cradle bolts, slotted along Y like the cradle's own base
    for (x = [-mb_pitch, mb_pitch]) translate([x, 0, 0]) slot(cradle_slot, m4_hole, "y");
    // camera lead
    translate([0, cable_y, 0]) slot(cable_l, cable_w, "y");
  }
}

strip();
