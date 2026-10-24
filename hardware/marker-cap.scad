// Marker cap for Grover's top (2026-10-24, Enoch: "maybe a bracket to hold
// Grover marker?" after the taped sheet curled up and the overhead lost it).
//
// A lid that friction-fits over the battery cradle's two long walls
// (battery-cradle.scad v3: outer width holder_w + clear_w + 2*wall_t =
// 66.6 mm) and carries the 60 mm ArUco id 2 marker on a flat top, FRONT
// toward the nose. The paper square (marker + 6 mm white margin, 72 x 72,
// cut from hardware/markers/aruco_4x4_50_id2_60mm.png) glues into a
// shallow recess; the plate around it stays white-ish for a quiet zone.
// Skirts grip only the long walls' outer faces, so both ends of the pocket
// (balance leads, BMS window) stay open; notches let the cradle's zip
// ties pass. Prints TOP FACE DOWN, no supports: the recess is a pocket in
// the first layers, the skirts rise as plain walls.
//
// ASSUMED: the cells stand <= 3 mm proud of the wall tops (body_h 17 in
// the cradle file was itself assumed; the lid sits 3 mm above the walls).

cradle_outer_w = 66.6;   // battery-cradle.scad: holder_w 61 + clear_w 0.6 + 2 * wall_t 2.5
holder_l       = 79;     // pocket length is holder_l + 4.6; skirts are shorter than that
fit            = 0.4;    // skirt inner width over the cradle's outer width
skirt_t        = 1.6;
skirt_len      = 56;     // along the holder, centred: clears both pocket ends by > 10 mm
grip_h         = 10;     // how far the skirts reach down the walls
cell_clear     = 3;      // lid underside above the wall tops (cells stand proud)
plate_t        = 2.4;
plate_w        = 78;     // across; >= 72 recess + rim
plate_l        = 78;     // along
recess         = 72.4;   // paper square 72 + play
recess_d       = 0.6;
tie_notch_w    = 7;      // the cradle's tie slots are 5 wide at y = +/- holder_l/4 from the pocket centre
tie_notch_d    = 3;

inner_w = cradle_outer_w + fit;
skirt_h = cell_clear + grip_h;

module cap() {
  difference() {
    union() {
      // plate, top at z = 0 (printed face), extends down to -plate_t
      translate([-plate_w / 2, -plate_l / 2, -plate_t]) cube([plate_w, plate_l, plate_t]);
      // skirts
      for (sx = [-1, 1])
        translate([sx * (inner_w / 2 + skirt_t / 2) - skirt_t / 2, -skirt_len / 2, -plate_t - skirt_h])
          cube([skirt_t, skirt_len, skirt_h + 0.01]);
    }
    // marker recess in the top face
    translate([-recess / 2, -recess / 2, -recess_d]) cube([recess, recess, recess_d + 1]);
    // zip-tie notches at the skirt bottoms
    for (sx = [-1, 1], sy = [-1, 1])
      translate([sx * (inner_w / 2 + skirt_t / 2), sy * holder_l / 4, -plate_t - skirt_h + tie_notch_d / 2 - 0.01])
        cube([skirt_t * 3, tie_notch_w, tie_notch_d], center = true);
    // FRONT arrow engraved in the rim, +y edge (the nose end)
    translate([0, plate_l / 2 - 2.2, -0.5]) linear_extrude(1) polygon([[-2.2, -1.2], [2.2, -1.2], [0, 1.2]]);
  }
}

// print orientation: flip so the top face is on the bed
translate([0, 0, plate_t + skirt_h]) mirror([0, 0, 1]) cap();

echo(str("marker cap: plate ", plate_w, "x", plate_l, "x", plate_t, "  skirts inner ", inner_w,
         " x ", skirt_len, " long, ", skirt_h, " deep (grip ", grip_h, ")  recess ", recess, " sq"));
