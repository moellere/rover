// Dock contact bar (2026-10-24, Enoch: "make contact plates that are
// perpendicular to the barrel contacts, to give some contact width").
// After run C the rollers sat at the cliff mounts' edges with a centimetre
// or two of lateral scatter run to run, more than a bolt head covers. This
// bar hangs on the pad plate's M4 (dock-pad-plate.scad) and runs ACROSS the
// roller: 32 mm of pad for a 10 mm roller.
//
// v2 (2026-10-25): the contact is a staple of bare 12 AWG solid copper
// (Romex ground; Enoch has no copper tape). The wire lies in a groove along
// the underside, standing ~1 mm proud so it is the lowest point, turns up
// through a hole at each end and lies in a groove on top back to the
// centre, where both legs wrap the bolt's shank under the nut - the bolt is
// then the conductor up to the ring terminal. The M4 comes up from below,
// its head in a pocket so it sits flush, not below the wire. Rotate the bar
// on the bolt to lie across the roller, then clamp. Two, one per side.
// Cut ~80 mm of wire per bar. Prints flat on its top face, no supports.

bar_l   = 32;
bar_w   = 12;
bar_t   = 5;
hole_d  = 4.4;
head_d  = 8.5;    // M4 pan head + play
head_h  = 3.2;    // pocket depth: head sits ~flush with the pad face
wire_d  = 2.05;   // 12 AWG bare solid
groove_w = 2.5;
under_depth = 1.0;    // wire stands wire_d - under_depth proud of the face
top_depth   = 2.2;    // legs lie just below the top face under the nut
leg_x   = 13;         // leg holes, from centre
leg_d   = 3.0;        // room for the bend radius
$fn = 48;

difference() {
  hull() for (x = [-bar_l / 2 + bar_w / 2, bar_l / 2 - bar_w / 2])
    translate([x, 0, 0]) cylinder(d = bar_w, h = bar_t);
  translate([0, 0, -1]) cylinder(d = hole_d, h = bar_t + 2);
  translate([0, 0, -0.01]) cylinder(d = head_d, h = head_h);   // head pocket on the underside (z = 0 face)
  // underside groove, end to end between the leg holes
  translate([-leg_x, -groove_w / 2, -0.01]) cube([2 * leg_x, groove_w, under_depth + 0.01]);
  // leg holes
  for (s = [-1, 1]) translate([s * leg_x, 0, -1]) cylinder(d = leg_d, h = bar_t + 2);
  // top grooves from each leg hole to the bolt
  translate([-leg_x, -groove_w / 2, bar_t - top_depth]) cube([2 * leg_x, groove_w, top_depth + 0.01]);
}
echo(str("dock pad bar v2 ", bar_l, " x ", bar_w, " x ", bar_t, ", 12 AWG staple, legs at +/-", leg_x,
         ", wire proud ", wire_d - under_depth, " mm"));
