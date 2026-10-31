// Battery tray: Grover's 3x18650 pack (holder + HW-288 BMS) behind the
// acrylic deck, spanning the two track rails (Enoch's design idea, 2026-10-31).
// It replaces battery cradle v3 on the posts, so the posts now carry only the
// fixed electronics top plate.
//
// Shape: a flange that rests on the tops of both track rails (a 2.5 mm lip
// on each, clear of the treads), with cradle v3's holder pocket ROTATED 90 deg
// (holder crosswise) and RECESSED between the rails: floor at ~40 mm above the
// bench, the pack's top about level with the rail tops (56 mm) - the lowest
// centre of gravity Grover has had. The BMS faces down through a floor window
// at the LEFT end (the rear motor, top at 32 mm, is on the right). Vertical
// tabs fill the gap between the pocket and each rail's inside face; they are
// SOLID - match-drill through the rail's own hole into the tab and bolt
// through (M4, nut on the outside face), so nothing has to line up with an
// unmeasured hole pattern. The right tab stops short of the rear motor plate
// (it covers the last ~31 mm of the rail). A low rear lip: lift the pack a
// little and slide it out the back. Two slots take a velcro strap over the pack.
//
// Frame: x across (+x = Grover's right), y REARWARD from the acrylic's rear
// edge, z up from the bench.
// Measured (Enoch, 10-31): rail tops 56 mm; rails 95 mm apart inside; 60 mm
// from the acrylic's rear edge to the rail ends; motor plate covers the rear
// ~31 mm of the right rail; rear motor top 32 mm. Holder + BMS 61 x 79 x ~23
// (10-19, as in battery-cradle.scad).
//
// Render: openscad -o battery-tray.stl battery-tray.scad
// Print:  floor down, no supports, no brim (the flange's longest overhang is
//         ~6 mm, on the right behind the short tab).

// holder (from battery-cradle.scad)
holder_w = 61;  holder_l = 79;  body_h = 17;  bms_h = 6;
bms_w = 45;     bms_l = 56;     clear_w = 0.6; clear_l = 4.6;

// chassis
rail_top   = 56;
rail_gap   = 95;       // inside faces
rail_len   = 60;       // acrylic rear edge -> rail ends
plate_cover = 31;      // right motor plate, from the rail end forward
lip        = 2.5;      // onto each rail top
flange_t   = 3;

// tray
wall_t   = 2.5;
floor_t  = 2.5;
floor_z  = 40;         // floor top above the bench (clears the 32 mm motor; BMS bottom at 34)
x_shift  = -1.5;       // pocket nudged left: more room beside the right motor plate
tab_gap  = 0.3;        // tab-to-rail clearance
tab_bot  = 34;         // tabs reach down to here (rail spans ~32-56)
rear_lip = 5;          // above the floor
y0       = 0.5;        // front face, just clear of the acrylic

inner_x = holder_l + clear_l;     // 83.6 across
inner_y = holder_w + clear_w;     // 61.6 front-back
px0 = x_shift - inner_x / 2;  px1 = x_shift + inner_x / 2;
py0 = y0 + wall_t;            py1 = py0 + inner_y;
ox0 = px0 - wall_t;           ox1 = px1 + wall_t;
oy1 = py1 + wall_t;
rail_x = rail_gap / 2;

$fn = 32;

module tray() {
  difference() {
    union() {
      // pocket body: floor and walls, up to the flange
      translate([ox0, y0, floor_z - floor_t]) cube([ox1 - ox0, oy1 - y0, rail_top + flange_t - (floor_z - floor_t)]);
      // flange over both rail tops, along the front and both sides
      translate([-rail_x - lip, y0, rail_top]) cube([rail_gap + 2 * lip, oy1 - y0, flange_t]);
      // tabs: fill pocket-to-rail, down the rails' inside faces
      translate([-rail_x + tab_gap, y0, tab_bot]) cube([ox0 + rail_x - tab_gap, rail_len - 2, rail_top - tab_bot]);
      translate([ox1, y0, tab_bot]) cube([rail_x - tab_gap - ox1, rail_len - plate_cover - 4, rail_top - tab_bot]);
    }
    // the pocket (open top), with the rear wall cut down to a low lip
    translate([px0, py0, floor_z]) cube([inner_x, inner_y, 50]);
    translate([px0, py1 - 1, floor_z + rear_lip]) cube([inner_x, wall_t + 2, 50]);
    // flange opening over the pocket
    translate([px0, py0, rail_top - 1]) cube([inner_x, inner_y + wall_t + 2, flange_t + 2]);
    // BMS window, left end of the floor
    translate([px0 + 2, py0 + (inner_y - bms_w - 6) / 2, floor_z - floor_t - 1]) cube([bms_l + 3, bms_w + 6, floor_t + 2]);
    // velcro strap slots (right half of the floor, front and rear)
    for (y = [py0 + 2, py1 - 5])
      translate([x_shift + 6, y, floor_z - floor_t - 1]) cube([24, 3, floor_t + 2]);
  }
}

module ghosts() {
  %translate([px0 + clear_l / 2, py0 + clear_w / 2, floor_z]) cube([holder_l, holder_w, body_h]);
  %for (s = [-1, 1]) translate([s * (rail_x + 4), rail_len / 2, rail_top - 12]) cube([8, rail_len, 24], center = true);
}

tray();
ghosts();
