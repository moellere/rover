// Battery cradle v3 for Grover (tank, 2026-10-19): the 3x18650 holder
// with the HW-288 3S 40A BMS soldered flush to one end of its back
// (Enoch: 61 x 79 x ~23 incl. the board; the power leads leave at the
// board end). Sits on the four 30 mm standoff posts over the
// controller/breadboard (102 x 71 outer -> 96 x 64 centres on the 8 mm
// grid, +/-2 mm slots). The posts are over the tank's front half, so the
// holder pocket is SHIFTED REARWARD on the post pattern by `shift` to
// move the pack's mass toward mid-track (Enoch's ask, 2026-10-19).
//
// Consequences of the shift: the rear bolts sit under the holder's
// floor, heads sunk below the floor surface (remove the holder to
// unbolt); the front bolts go through the floor-level front tab, which
// is also the camera perch (M4 grid, 8 mm pitch). The BMS goes at the
// FRONT end of the pocket: its window is open to the deck below, so the
// leads drop straight down to the buck converter. Cells face up.
//
// Print: floor down, no supports.
// ASSUMED: body_h 17 (holder plastic only), bms_h 6, posts M4.

// ---- Holder with BMS flush at one end of its back (measured) -------------
holder_w  = 61;
holder_l  = 79;
body_h    = 17;      // ASSUMED
bms_h     = 6;       // ASSUMED
bms_w     = 45;      // HW-288 56 x 45
bms_l     = 56;
clear_w   = 0.6;
clear_l   = 4.6;     // the balance leads wrap around both ends (2 mm each)

// ---- Posts --------------------------------------------------------------
post_cc_l = 96;      // along (y), +y = rear
post_cc_w = 64;      // across (x)
slot      = 2;
m4_hole   = 4.5;
head_d    = 8.5;
head_h    = 4.5;     // socket cap sunk below the floor top (rear bolts)

// ---- Frame --------------------------------------------------------------
shift     = 40;      // pocket centre rearward of the post centre (5 pitches): puts the pack on the track midpoint (top photo, 2026-10-19)
wall_t    = 2.5;
end_t     = 6;
floor_t   = 8;       // thick enough to sink the rear bolt heads (3.5 mm left)
win_w     = bms_w + 6;
win_l     = bms_l + 3;
tie_w     = 5; tie_t = 2.2;

// ---- Front tab: front bolts + camera perch -------------------------------
tab_w     = 80;      // covers the front bolts at x = +/-32
perch_rows = [-8, 0];   // camera grid rows, relative to perch_y
perch_cols = [-24, -16, -8, 0, 8, 16, 24];

inner_w = holder_w + clear_w;
inner_l = holder_l + clear_l;
outer_w = inner_w + 2 * wall_t;
pocket_front = shift - inner_l / 2;
pocket_rear  = shift + inner_l / 2;
body_front = pocket_front - end_t;
body_rear  = pocket_rear + end_t;
top_h   = floor_t + body_h;
front_bolt_y = -post_cc_l / 2;
rear_bolt_y  =  post_cc_l / 2;
tab_front = front_bolt_y - 38;             // room for the bolt, the camera grid and the camera base (44 long) ahead of it
perch_y   = front_bolt_y - 12;             // camera grid centre row

module rbox(w, l, h, r = 2) { linear_extrude(h) offset(r) offset(-r) square([w, l], center = true); }
module ybox(w, y0, y1, h, r = 2) { translate([0, (y0 + y1) / 2, 0]) rbox(w, y1 - y0, h, r); }

difference() {
  union() {
    ybox(outer_w, body_front, body_rear, top_h);           // body
    ybox(tab_w, tab_front, body_front + 10, floor_t);      // front tab (bolts + perch), overlaps the body
    ybox(tab_w, rear_bolt_y - 8, rear_bolt_y + 8, top_h);   // side blocks at the rear bolts so their counterbores stay enclosed
  }
  // holder pocket
  translate([0, shift, floor_t]) rbox(inner_w, inner_l, body_h + 1, 1);
  // BMS window at the FRONT end of the pocket, open to the deck below
  translate([0, pocket_front + win_l / 2, -1]) rbox(win_w, win_l, floor_t + 2, 2);
  // bolts: slotted holes everywhere; counterbores on the rear pair (sunk below the floor top)
  for (sx = [-1, 1], y = [front_bolt_y, rear_bolt_y]) {
    hull() for (dy = [-slot / 2, slot / 2])
      translate([sx * post_cc_w / 2, y + dy, -1]) cylinder(d = m4_hole, h = top_h + 2, $fn = 24);
  }
  for (sx = [-1, 1])
    hull() for (dy = [-slot / 2, slot / 2])
      translate([sx * post_cc_w / 2, rear_bolt_y + dy, floor_t - head_h]) cylinder(d = head_d, h = top_h, $fn = 32);
  // zip-tie slots through the long walls, two straps over the cells
  for (sy = [-1, 1], sx = [-1, 1])
    translate([sx * outer_w / 2, shift + sy * holder_l / 4, floor_t + 2 + tie_w / 2])
      cube([wall_t * 3, tie_t, tie_w], center = true);
  // camera cable drop under the camera base's slot (camera-mount v6 on the rear grid row, usb_x = 0)
  hull() for (y = [perch_y + 3 - 1.5, perch_y + 3 + 1.5]) translate([0, y, -1]) cylinder(d = 13, h = floor_t + 2, $fn = 32);
  // camera perch grid
  for (x = perch_cols, dy = perch_rows)
    translate([x, perch_y + dy, -1]) cylinder(d = m4_hole, h = floor_t + 2, $fn = 24);
}
// sanity echoes
echo(str("pocket y ", pocket_front, "..", pocket_rear, "  window rear edge ", pocket_front + win_l,
         "  rear bolt cbore from ", rear_bolt_y - head_d / 2 - slot / 2, "  body y ", tab_front, "..", body_rear));
