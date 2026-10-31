// Battery tray: Grover's 3x18650 pack (holder + HW-288 BMS) behind the
// acrylic deck, ON TOP of the two track rails (Enoch's design, 2026-10-31).
// It replaces battery cradle v3 on the posts, so the posts now carry only the
// fixed electronics top plate.
//
// Shape (v2 - v1 recessed the pocket between the rails, and Enoch: "it
// definitely won't be able to sit that low - the motor will interfere"):
// a floor plate that rests on both rail tops (2.5 mm onto each, clear of the
// treads), with cradle v3's holder pocket ROTATED 90 deg (holder crosswise) on
// top of it. Only the BMS (through its floor window, ~6 mm) and the tabs reach
// below the rail tops. The BMS sits at the LEFT end (the rear motor is on the
// right). Vertical tabs hang down the rails' inside faces; they are SOLID -
// match-drill through the rail's own hole into the tab and bolt through (M4,
// nut on the outside face), so nothing has to line up with an unmeasured hole
// pattern. The right tab stops short of the rear motor plate (it covers the
// last ~31 mm of the rail). A low rear lip: lift the pack a little and slide it
// out the back. Two slots take a velcro strap over the pack.
//
// Frame: x across (+x = Grover's right), y REARWARD from the acrylic's rear
// edge, z up from the bench.
// Measured (Enoch, 10-31): rail tops 56 mm; rails 95 mm apart inside; 60 mm
// from the acrylic's rear edge to the rail ends; motor plate covers the rear
// ~31 mm of the right rail. Holder + BMS 61 x 79 x ~23 (10-19; body 17 / BMS 6
// are the cradle's assumed split).
//
// Render: openscad -o battery-tray.stl battery-tray.scad
// Print:  floor down, no supports, no brim.

// holder (from battery-cradle.scad)
holder_w = 61;  holder_l = 79;  body_h = 17;  bms_h = 6;
bms_w = 45;     bms_l = 56;     clear_w = 0.6; clear_l = 4.6;

// chassis
rail_top    = 56;
rail_gap    = 95;      // inside faces
rail_len    = 60;      // acrylic rear edge -> rail ends
plate_cover = 31;      // right motor plate, from the rail end forward
lip         = 2.5;     // floor overhang onto each rail top

// tray
floor_t  = 3;
wall_t   = 2.5;
wall_h   = 14;         // pocket walls above the floor (holder body ~17)
rear_lip = 5;
tab_t    = 3;
tab_gap  = 0.3;        // tab-to-rail clearance
tab_drop = 12;         // tabs reach this far below the rail tops: the top row of holes only (Enoch)
y0       = 0.5;        // front face, just clear of the acrylic

inner_x = holder_l + clear_l;     // 83.6 across
inner_y = holder_w + clear_w;     // 61.6 front-back
px0 = -inner_x / 2;  px1 = inner_x / 2;
py0 = y0 + wall_t;   py1 = py0 + inner_y;
oy1 = py1 + wall_t;
rail_x = rail_gap / 2;
fz = rail_top + floor_t;          // floor top

$fn = 32;

module tray() {
  difference() {
    union() {
      // floor plate over both rails
      translate([-rail_x - lip, y0, rail_top]) cube([rail_gap + 2 * lip, oy1 - y0, floor_t]);
      // pocket walls
      translate([px0 - wall_t, y0, fz]) cube([inner_x + 2 * wall_t, oy1 - y0, wall_h]);
      // tabs down the rails' inside faces
      translate([-rail_x + tab_gap, y0, rail_top - tab_drop]) cube([tab_t, rail_len - 2, tab_drop + 0.01]);
      translate([rail_x - tab_gap - tab_t, y0, rail_top - tab_drop]) cube([tab_t, rail_len - plate_cover - 4, tab_drop + 0.01]);
    }
    // the pocket, open top; rear wall cut down to a low lip
    translate([px0, py0, fz]) cube([inner_x, inner_y, 50]);
    translate([px0, py1 - 1, fz + rear_lip]) cube([inner_x, wall_t + 2, 50]);
    // BMS window, left end of the floor
    translate([px0 + 2, py0 + (inner_y - bms_w - 6) / 2, rail_top - 1]) cube([bms_l + 3, bms_w + 6, floor_t + 2]);
    // velcro strap slots (right half of the floor, front and rear)
    for (y = [py0 + 2, py1 - 5])
      translate([6, y, rail_top - 1]) cube([24, 3, floor_t + 2]);
  }
}

module ghosts() {
  %translate([px0 + clear_l / 2, py0 + clear_w / 2, fz]) cube([holder_l, holder_w, body_h]);
  %for (s = [-1, 1]) translate([s * (rail_x + 4), rail_len / 2, rail_top - 12]) cube([8, rail_len, 24], center = true);
}

tray();
ghosts();
