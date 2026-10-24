// Dock contact pad carrier (2026-10-24). Grover docks on the Eufy base; its
// two sprung rollers end up under the deck plate's hole grid, but not under
// a free hole (Enoch: "slightly offset towards the center and rearwards",
// unmeasurable with Grover in place). So: a small plate that bolts through
// ANY deck hole 10..24 mm from the roller and carries the contact bolt in a
// radial slot - rotate the plate about the deck bolt and slide the pad bolt
// along the slot, and the pad reaches any point in that ring. Tighten both
// and it stays.
//
// Contact: an M4 bolt, head DOWN, through the slot, clamped above and below
// the plate by two nuts (height = how far it hangs, set by the nuts), a
// 16-20 mm fender washer under the head as the pad face, ring terminal for
// the wire under the top nut. Two plates, one per side; mirror-symmetric
// so one print x2.
//
// Prints flat, no supports.

plate_t   = 4;
plate_w   = 14;          // across the slot
r_min     = 10;          // pad bolt centre, nearest to the deck bolt (nut clearance)
r_max     = 24;          // ... farthest
deck_hole = 4.5;         // M4 clearance
slot_w    = 4.5;
end_r     = plate_w / 2;
nut_af    = 7.2;         // M4 nut across flats + play: a hex pocket under the deck bolt
                         // so the deck nut can't turn while you tighten from above
nut_h     = 2.5;

$fn = 48;

module plate() {
  difference() {
    hull() {
      cylinder(r = end_r, h = plate_t);
      translate([r_max, 0, 0]) cylinder(r = end_r, h = plate_t);
    }
    // deck bolt
    translate([0, 0, -1]) cylinder(d = deck_hole, h = plate_t + 2);
    // hex pocket for its nut, from below
    translate([0, 0, -0.01]) cylinder(d = nut_af / cos(30), h = nut_h, $fn = 6);
    // radial slot for the pad bolt
    hull() for (x = [r_min, r_max - 2])
      translate([x, 0, -1]) cylinder(d = slot_w, h = plate_t + 2);
  }
}

plate();
echo(str("dock pad plate: ", r_max + end_r, " x ", plate_w, " x ", plate_t, " mm, slot ", r_min, "..", r_max - 2, " mm from the deck bolt"));
