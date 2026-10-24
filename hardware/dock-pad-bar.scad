// Dock contact bar (2026-10-24, Enoch: "make contact plates that are
// perpendicular to the barrel contacts, to give some contact width").
// After run C the rollers sat at the cliff mounts' edges with a centimetre
// or two of lateral scatter run to run, more than a bolt head covers. This
// bar hangs on the pad plate's M4 (dock-pad-plate.scad) and runs ACROSS the
// roller: 32 mm of pad for a 10 mm roller. The bolt comes up from below
// through the bar, its head recessed in a pocket on the underside so the
// contact face is flat; copper tape (or a brass strip) is laid over the
// underside and wrapped up the ends, touching the bare bolt head in its
// pocket - the bolt is the conductor up to the ring terminal. Rotate the
// bar on the bolt to lie across the roller, then clamp. Two, one per side.
// Prints flat on its top face, no supports.

bar_l   = 32;
bar_w   = 12;
bar_t   = 5;
hole_d  = 4.4;
head_d  = 8.5;    // M4 pan head + play
head_h  = 3.2;    // pocket depth: head sits ~flush with the pad face
$fn = 48;

difference() {
  hull() for (x = [-bar_l / 2 + bar_w / 2, bar_l / 2 - bar_w / 2])
    translate([x, 0, 0]) cylinder(d = bar_w, h = bar_t);
  translate([0, 0, -1]) cylinder(d = hole_d, h = bar_t + 2);
  translate([0, 0, -0.01]) cylinder(d = head_d, h = head_h);   // head pocket on the underside (z = 0 face)
}
echo(str("dock pad bar ", bar_l, " x ", bar_w, " x ", bar_t, ", head pocket ", head_d, " x ", head_h));
