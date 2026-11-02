// Dock approach ramp (2026-11-01, Enoch's idea): a printed wedge that butts
// against the front edge of the dock (the Eufy base) so Grover's tracks roll
// up a gentle slope instead of hitting the base's rounded lip - the lip made
// every climb lurch, yaw Grover 4-6 deg and land off the rollers.
//
// Measured (Enoch, 11-01): base front edge 165 mm wide, corners rounded in
// plan; its lowest (front) edge ~6 mm above the bench, rising to ~11 mm where
// the tracks ride (journal 10-24). Cliff sensors' lowest point 12 mm above
// the bench and 65 mm ahead of where the tracks touch the bench.
//
// Slope: before the tracks start to climb, a sensor 65 mm ahead sees the
// ramp rise by slope x 65 mm. Keeping >= 3 mm under it allows <= 9/65 (14 %).
// 6 mm over 80 mm is 7.5 %: ~7 mm of clearance at the worst point, and a
// gentle enough start that one track can't snatch the lip before the other.
//
// Frame: +y toward the dock (the ramp's high, butt end at y = ramp_l), x
// across, z up from the bench.
//
// Render: openscad -o dock-ramp.stl dock-ramp.scad
// Print:  flat (bottom on the bed), no supports, no brim. Tape it to the bench
//         with its butt end against the base's front edge.

ramp_w   = 165;    // = the base's front edge
ramp_l   = 80;
h_butt   = 6.0;    // the base's front edge height
h_toe    = 0.6;    // printable feather edge
corner_r = 15;     // butt-end corners rounded - NOTE (11-01, Enoch spotted it): rounded the same way as the
                   // base's front corners, not mirrored, so ~15 mm gaps at the two corners; the straight
                   // middle 135 mm meets the base flush. A v2 could wrap them instead.
rib_h    = 0.6;    // grip ribs across the slope (smooth PETG slips like paper)
rib_w    = 1.2;
rib_p    = 6;

$fn = 48;

function hz(y) = h_toe + (h_butt - h_toe) * y / ramp_l;

module outline() {
  // rounded corners at the butt end only
  hull() {
    translate([-ramp_w / 2, 0]) square([ramp_w, 1]);
    for (sx = [-1, 1]) translate([sx * (ramp_w / 2 - corner_r), ramp_l - corner_r]) circle(r = corner_r);
  }
}

module wedge() {
  intersection() {
    linear_extrude(h_butt + rib_h + 1) outline();
    // the slope: a prism under the plane z = hz(y)
    rotate([90, 0, 90]) translate([0, 0, -ramp_w]) linear_extrude(2 * ramp_w)
      polygon([[0, 0], [ramp_l, 0], [ramp_l, h_butt], [0, h_toe]]);
  }
}

module ribs() {
  intersection() {
    linear_extrude(h_butt + rib_h + 1) offset(delta = -3) outline();
    for (y = [rib_p : rib_p : ramp_l - rib_p])
      translate([-ramp_w / 2, y - rib_w / 2, 0])
        cube([ramp_w, rib_w, hz(y) + rib_h]);
  }
}

wedge();
ribs();

echo(str("dock ramp: ", ramp_w, " x ", ramp_l, ", ", h_toe, " -> ", h_butt, " mm (", round(1000 * (h_butt - h_toe) / ramp_l) / 10,
         " %); sensor clearance at the worst point ~", 12 - (h_butt - h_toe) / ramp_l * 65, " mm"));
