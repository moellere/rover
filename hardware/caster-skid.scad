// Caster skid: replaces Grover's swivel caster with a fixed, domed PETG
// skid. The swivel caster twisted the rear on stops (2026-10-05: with the
// caster zip-tied straight, Grover stopped square; free, it yawed 20-30 deg).
// A round skid is rotationally symmetric, so the single mounting bolt can't
// "steer" it.
//
// Mounting: the caster hung from one threaded stem through a 5.5 mm hole
// in the blue Makeblock block, bracket underside 36 mm above the bench
// (Enoch's measurements). Here: an M5 bolt goes down through that hole and
// into a captive M5 nut, slid into the skid through a side slot.
//
// Print: on its flat TOP face, dome up. The nut slot's roof is a ~9 mm
// bridge, which PETG handles without supports. No brim.
//
// Render:  openscad -o caster-skid.stl caster-skid.scad

height    = 36;     // bracket underside to bench (Enoch, 2026-10-05)
dia       = 22;     // puck diameter
dome_h    = 6;      // spherical-cap height of the sliding face
bolt_d    = 5.5;    // M5 clearance
nut_af    = 8.2;    // M5 nut across flats + clearance
nut_t     = 4.4;    // M5 nut thickness + clearance
nut_z     = 12;     // nut pocket depth below the top face
$fn = 72;

// spherical cap radius for a cap of height dome_h on a base of radius dia/2
cap_r = (pow(dia / 2, 2) + pow(dome_h, 2)) / (2 * dome_h);

module skid() {
  difference() {
    union() {
      // body: from the dome base up to the top face
      translate([0, 0, dome_h]) cylinder(d = dia, h = height - dome_h);
      // dome (sliding face) at the bottom, z = 0 .. dome_h
      intersection() {
        translate([0, 0, cap_r]) sphere(r = cap_r);
        cylinder(d = dia, h = dome_h + 0.01);
      }
    }
    // bolt hole from the top down past the nut
    translate([0, 0, height - nut_z - 8]) cylinder(d = bolt_d, h = nut_z + 9);
    // captive nut pocket, open to one side
    translate([0, 0, height - nut_z - nut_t / 2])
      hull() {
        cylinder(d = nut_af / cos(30), h = nut_t, $fn = 6);
        translate([dia, 0, 0]) cylinder(d = nut_af / cos(30), h = nut_t, $fn = 6);
      }
  }
}

// print orientation: top face down
translate([0, 0, height]) rotate([180, 0, 0]) skid();
