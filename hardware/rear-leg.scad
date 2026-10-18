// Rear leg + skid for Grover, replacing the Makeblock L-bracket that
// sheared at its bend in the 2026-10-18 fall (and the separate printed
// skid that hung from it). One PETG piece: a vertical plate that bolts to
// the two M4 socket-cap bolts left on the rear beam stub, a web down to a
// foot, and the domed skid grown out of the foot's underside. No bent
// joint, no second part to lose.
//
// Load case: the skid takes a sideways drag on every stop and pivot, so
// the web is a full-width wedge (thick at the plate, tapering to the
// foot), not a thin arm.
//
// Print: lying on its BACK (the plate face on the bed), dome pointing up
// and sideways -> no supports with the 45 deg wedge. Modelled upright for
// readability; rotate in the slicer or use the print module below.
//
// ASSUMED until Enoch measures (2026-10-18): bolt_cc, bolt_h, plate_w.

// ---- Interface to the beam stub (Makeblock 8 mm grid, M4) ---------------
bolt_cc   = 16;    // the two socket caps, centre to centre        (ASSUMED)
bolt_h    = 50;    // their centreline above the bench, rover level (ASSUMED)
m4_hole   = 4.5;
plate_w   = 32;    // plate width across the bolts (bolt_cc + 2*8)
plate_h   = 24;    // plate height, bolts on its mid-line
plate_t   = 6;

// ---- Leg and skid -----------------------------------------------------
foot_d    = 22;    // same dome as caster-skid.scad
dome_r    = 11;
foot_t    = 6;     // flat part of the foot above the dome
setback   = 12;    // skid centre behind the plate face (rearward)
web_t     = 10;    // web thickness at the plate, tapers to the foot

leg_h = bolt_h - plate_h / 2;             // plate bottom edge to bench
ground_to_foot = leg_h - dome_r - foot_t;  // height of the web

module leg() {
  // plate, bolts on the mid-line, z=0 at the bench, y+ = rearward
  difference() {
    translate([-plate_w / 2, 0, bolt_h - plate_h / 2]) cube([plate_w, plate_t, plate_h]);
    for (x = [-bolt_cc / 2, bolt_cc / 2])
      translate([x, -1, bolt_h]) rotate([-90, 0, 0]) cylinder(d = m4_hole, h = plate_t + 2, $fn = 24);
  }
  // wedge web: full plate width at the top, foot width at the bottom
  hull() {
    translate([-plate_w / 2, 0, bolt_h - plate_h / 2]) cube([plate_w, web_t, 0.01]);
    translate([0, setback, dome_r + foot_t]) cylinder(d = foot_d, h = 0.01, $fn = 48);
  }
  // foot + dome
  translate([0, setback, dome_r]) {
    cylinder(d = foot_d, h = foot_t, $fn = 48);
    sphere(r = dome_r, $fn = 48);
  }
}

// print orientation: plate face down on the bed
module print_leg() { rotate([90, 0, 0]) leg(); }

print_leg();
