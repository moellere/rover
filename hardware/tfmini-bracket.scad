// TFMini bracket: holds the Benewake TFMini (SparkFun Qwiic, SEN-14786)
// in front of Grover's front cross beam, lenses forward, centred and level
// at the beam's mid-height.
//
// It sits on the beam's TOP face and bolts through the two beam holes next
// to the centre pair (x = +/-12 mm); the centre pair is taken by the bracket
// under the beam that joins the cross beam to the caster beam, so their
// screw heads / nuts on top sit in a relief pocket under this part. Beam
// holes are plain M4 through-holes: M4 screw from the top, nut underneath.
// A plate drops in front of the beam's front face and carries the sensor
// by its two ears (M2).
//
// Frame: X across the rover, +Y forward (travel), +Z up. Origin = the
// beam's top-front edge at the rover's centreline.
//
// Print: lying on the sensor plate's FRONT face (the flat face the TFMini
// bolts to goes down on the bed) - the tabs then stand up, no supports,
// no brim.
//
// Render:  openscad -o tfmini-bracket.stl tfmini-bracket.scad

// ---- TFMini (Benewake drawing, TFmini/TFmini-S housing) --------------------
tf_len     = 42;     // ear tip to ear tip
tf_body_w  = 33;     // body between the ears
tf_h       = 15;     // body height on the mounting face
tf_ear_cc  = 36;     // ear hole centre-to-centre
tf_ear_d   = 2.35;   // ear hole (M2)
m2_pilot   = 2.0;    // M2 machine screw threads itself into PETG

// ---- Beam (Makeblock 0824, lying flat; ASSUMED, check on the part) --------
beam_depth = 24;     // top face, front-to-back
beam_h     = 8;      // front face height
hole_x     = 12;     // next hole out from the centre pair (8 mm grid)
hole_y     = -12;    // hole row on the top face's centreline
m4_hole    = 4.5;    // clearance, oversized like the camera strip
slot_adj   = 2.0;    // +/- front-back play in case the row isn't centred

// ---- Centre-pair relief (nuts / heads of the under-beam bracket) ----------
relief_w   = 17;     // x = +/-8.5 clears an M4 nut at x = +/-4 (8.1 mm AF-corners)
relief_h   = 5;      // M4 nut 3.2 mm + stub of screw

// ---- Bracket ----------------------------------------------------------------
base_top   = relief_h + 3;   // 3 mm bridge over the relief
base_w     = 2 * (hole_x + 7);
plate_t    = 4;              // sensor plate thickness (Y)
plate_w    = tf_len + 4;
sensor_zc  = -beam_h / 2;    // sensor centre = beam mid-height
plate_bot  = sensor_zc - tf_h / 2 - 2;

$fn = 40;

module base() {
  difference() {
    translate([-base_w / 2, -beam_depth, 0]) cube([base_w, beam_depth, base_top]);
    // relief over the centre pair
    translate([-relief_w / 2, -beam_depth - 1, -1]) cube([relief_w, beam_depth + 2, relief_h + 1]);
    // M4 slots, front-back
    for (s = [-1, 1]) hull() for (dy = [-slot_adj, slot_adj])
      translate([s * hole_x, hole_y + dy, -1]) cylinder(d = m4_hole, h = base_top + 2);
  }
}

module plate() {
  difference() {
    translate([-plate_w / 2, 0, plate_bot]) cube([plate_w, plate_t, base_top - plate_bot]);
    // ear holes, through Y
    for (s = [-1, 1])
      translate([s * tf_ear_cc / 2, -1, sensor_zc]) rotate([-90, 0, 0])
        cylinder(d = m2_pilot, h = plate_t + 2);
  }
}

// TFMini ghost for visual checks only (not exported): body on the plate front.
module tfmini_ghost() {
  translate([-tf_body_w / 2, plate_t, sensor_zc - tf_h / 2]) cube([tf_body_w, 11, tf_h]);
  for (x = [-5, 5]) translate([x, plate_t + 11, sensor_zc]) rotate([-90, 0, 0]) cylinder(d = 10, h = 5);
}

// print_orient: lay it on the sensor plate's front face (+Y -> -Z)
print_orient = true;
if (print_orient) {
  rotate([-90, 0, 0]) translate([0, -plate_t, 0]) { base(); plate(); }
} else {
  base(); plate();
  %tfmini_ghost();
}
