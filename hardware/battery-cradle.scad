// Battery cradle for Grover's 3S pack: the 3x18650 holder with the HW-288
// 3S 40A BMS soldered to its back (Enoch, 2026-10-18: 61 wide x 79 long x
// ~23 high including the board). Sits on the four standoff posts over the
// motor controller / breadboard (Enoch's call: the rear plate stacked the
// pack's ~200 g over the skid). Posts measured 102 x 71 mm outer-to-outer
// -> 95 x 64 centres for 7 mm standoffs; modelled 96 x 64 on the 8 mm
// grid with +/-2 mm slots. Cells face UP (swappable); the BMS on the
// holder's back drops into a window in the floor and is flush with the
// floor's underside, so nothing hangs below the post tops.
//
// Front edge carries a perch for the camera cradle: a flat tab with M4
// holes on the 8 mm grid (the v5 base used two at 16 mm c-c; a v6 base
// can use any of them).
//
// Print: floor down, no supports (counterbores open upward, zip-tie
// slots are 2 mm bridges).
//
// ASSUMED: body_h 17 (holder plastic only), bms_h 6, post thread M4.

// ---- Holder with BMS on its back (measured) ----------------------------
holder_w  = 61;      // across the cells (x)
holder_l  = 79;      // along the cells (y)
body_h    = 17;      // holder plastic, open face to back          (ASSUMED)
bms_h     = 6;       // board + parts proud of the holder's back    (ASSUMED)
bms_w     = 45;      // HW-288 56 x 45, centred on the back
bms_l     = 56;
bms_gap   = 0;       // board edge to the holder's end: FLUSH (Enoch, 2026-10-18), the leads leave at that end; that end goes to the rear (+y)
clear     = 0.6;

// ---- Posts (Makeblock 8 mm grid, M4) ----------------------------------
post_cc_l = 96;      // along the chassis (y): 102 outer - 7 = 95 -> 96
post_cc_w = 64;      // across (x): 71 outer - 7 = 64
slot      = 2;       // +/- along y, takes up the 95-vs-96
m4_hole   = 4.5;
head_d    = 8.5;     // socket/pan head counterbore
head_h    = 4;

// ---- Frame --------------------------------------------------------------
wall_t    = 2.5;
floor_t   = bms_h;   // BMS flush with the underside
end_t     = 14;      // thick end walls carry the post bolts
end_w     = 80;      // end blocks wider than the body so the counterbores stay enclosed
win_w     = bms_w + 6;
win_l     = bms_l + 3;                  // 3 mm clear at the front; the rear edge is the pocket's end wall
win_y_c   = ((holder_l + clear) / 2 - bms_gap) - win_l / 2;   // rear edge of the window = the pocket's rear wall
tie_w     = 5; tie_t = 2.2;

// ---- Camera perch (front = -y) -------------------------------------------
perch_d   = 28;      // how far the tab reaches forward of the end wall
perch_w   = 48;

inner_w = holder_w + clear;
inner_l = holder_l + clear;
outer_w = inner_w + 2 * wall_t;
outer_l = inner_l + 2 * end_t;        // bolts at +/-48 sit inside 12 mm end walls
top_h   = floor_t + body_h;

module rbox(w, l, h, r = 2) { linear_extrude(h) offset(r) offset(-r) square([w, l], center = true); }

difference() {
  union() {
    rbox(outer_w, outer_l, top_h);                                        // body
    for (sy = [-1, 1]) translate([0, sy * (outer_l / 2 - end_t / 2), 0]) rbox(end_w, end_t, top_h);  // end blocks
    translate([0, -(outer_l / 2 + perch_d / 2), 0]) rbox(perch_w, perch_d + 4, floor_t);   // perch tab
  }
  // holder pocket
  translate([0, 0, floor_t]) rbox(inner_w, inner_l, body_h + 1, 1);
  // BMS window through the floor
  translate([0, win_y_c, -1]) rbox(win_w, win_l, floor_t + 2, 2);
  // post bolts: slotted holes + counterbores from the top of the end walls
  for (sx = [-1, 1], sy = [-1, 1]) {
    hull() for (dy = [-slot / 2, slot / 2])
      translate([sx * post_cc_w / 2, sy * post_cc_l / 2 + dy, -1]) cylinder(d = m4_hole, h = top_h + 2, $fn = 24);
    hull() for (dy = [-slot / 2, slot / 2])
      translate([sx * post_cc_w / 2, sy * post_cc_l / 2 + dy, head_h]) cylinder(d = head_d, h = top_h, $fn = 32);
  }
  // zip-tie slots through the long walls, two straps over the cells
  for (sy = [-1, 1], sx = [-1, 1])
    translate([sx * outer_w / 2, sy * holder_l / 4, floor_t + 2 + tie_w / 2])
      cube([wall_t * 3, tie_t, tie_w], center = true);
  // perch holes: 8 mm grid, two rows x five
  for (x = [-16, -8, 0, 8, 16], y = [-8, 0])
    translate([x, -(outer_l / 2 + 8) + y, -1]) cylinder(d = m4_hole, h = floor_t + 2, $fn = 24);
  // lead exit: full-height slot through the rear end wall, down to the
  // underside - the leads leave the board at floor level, at that end
  translate([0, outer_l / 2 - end_t / 2, top_h / 2]) cube([12, end_t + 2, top_h + 2], center = true);
}
