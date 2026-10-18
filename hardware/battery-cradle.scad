// Battery cradle for Grover's 3S pack: the 3x18650 holder with the HW-288
// 3S 40A BMS soldered to its back (Enoch, 2026-10-18: 61 wide x 79 long x
// ~23 high including the board). Replaces the bare holder on the rear
// Makeblock plate; the holder sits in this frame with the cells facing
// outward (away from the plate) so they can still be swapped, and the BMS
// pokes through a window in the frame's floor into a gap between the
// floor and the plate. Four M4 slots on the plate's 8 mm grid, two zip-tie
// slots per side wall to strap the holder in.
//
// Print: open ring face DOWN (as modelled: z=0 is the open face, the plate
// side is at the top). The floor's underside is chamfered 45 deg so it needs
// no supports; the feet grow straight up from the ears.
//
// Unknowns to confirm on the part: body_h (holder plastic without the
// board - 17 assumed from the photos; the 23 total includes the board),
// bms_h (board + MOSFETs standing proud of the holder's back, 6 assumed).
// Both only move the floor/feet heights; the fit is set by holder_w/l.

// ---- Holder with BMS on its back (measured) --------------------------------
holder_w  = 61;      // across the cells (x)
holder_l  = 79;      // along the cells (y)
body_h    = 17;      // holder plastic only, open face to back  (ASSUMED)
bms_h     = 6;       // board + parts standing proud of the back (ASSUMED)
bms_w     = 45;      // HW-288 board, 56 x 45 (datasheet), centred on the back
bms_l     = 56;
clear     = 0.6;     // total clearance around the holder

// ---- Frame -----------------------------------------------------------------
wall_t    = 2.5;
floor_t   = 3;
gap       = bms_h + 2;    // floor to plate: board plus wire room
win_w     = bms_w + 6;    // BMS window, generous: the leads come off its edges
win_l     = bms_l + 6;

// ---- Plate interface (Makeblock 8 mm grid, M4) -----------------------------
mb_pitch  = 8;
m4_hole   = 4.5;
ear_w     = 12;           // ear tab beyond the wall
ear_y     = 3 * mb_pitch; // bolt rows at y = +/-24 (3 pitches apart from centre)
ear_slot  = 3;            // extra slot length along x, tolerates the grid offset

inner_w = holder_w + clear;
inner_l = holder_l + clear;
outer_w = inner_w + 2 * wall_t;
outer_l = inner_l + 2 * wall_t;
bolt_x  = outer_w / 2 + ear_w / 2;
total_h = body_h + floor_t + gap;
tie_w   = 5; tie_t = 2.2;  // zip-tie slot

module rounded_box(w, l, h, r = 2) {
  linear_extrude(h) offset(r) offset(-r) square([w, l], center = true);
}

module ears() {
  for (sx = [-1, 1], sy = [-1, 1])
    translate([sx * bolt_x, sy * ear_y, 0])
      hull() for (dx = [-ear_slot / 2, ear_slot / 2])
        translate([dx, 0, 0]) cylinder(d = ear_w, h = total_h, $fn = 40);
}

difference() {
  union() {
    rounded_box(outer_w, outer_l, body_h + floor_t);          // walls + floor
    // ears: flat tabs at floor level, continuing up as feet to the plate
    intersection() {
      ears();
      // only above the floor's underside, so nothing hangs below the walls
      translate([-100, -100, body_h - 2]) cube([200, 200, 100]);
    }
    // web joining each ear to the wall over the floor's height
    for (sx = [-1, 1], sy = [-1, 1])
      translate([sx * (outer_w / 2 + ear_w / 4), sy * ear_y, body_h - 2])
        cube([ear_w / 2 + 0.1, ear_w, floor_t + 2], center = false ? false : true);
  }
  // holder pocket
  translate([0, 0, -1]) rounded_box(inner_w, inner_l, body_h + 1, 1);
  // BMS window through the floor, chamfered 45 deg on the open side
  hull() {
    translate([0, 0, body_h - 0.01]) rounded_box(win_w, win_l, 0.02, 2);
    translate([0, 0, body_h - 12]) rounded_box(win_w + 24, win_l + 24, 0.02, 2);
  }
  translate([0, 0, body_h - 0.01]) rounded_box(win_w, win_l, 50, 2);
  // M4 slots down the feet
  for (sx = [-1, 1], sy = [-1, 1])
    translate([sx * bolt_x, sy * ear_y, 0])
      hull() for (dx = [-ear_slot / 2, ear_slot / 2])
        translate([dx, 0, -1]) cylinder(d = m4_hole, h = total_h + 2, $fn = 24);
  // zip-tie slots through both long walls, two straps along the holder
  for (sy = [-1, 1], sx = [-1, 1])
    translate([sx * (outer_w / 2), sy * (holder_l / 4), 2 + tie_w / 2])
      cube([wall_t * 3, tie_t, tie_w], center = true);
}
