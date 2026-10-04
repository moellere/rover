// Cliff sensor mount (one per side, mirrored): hangs an HW-870 / TCRT5000
// reflectance module ahead of a front wheel, sensor face a few mm above the
// bench, from the end holes of the front cross beam.
//
// Shape: an L. A foot bolts to the beam's TOP face through two M4 holes of
// one row (16 mm apart along the beam). A plate drops down in front of the
// beam's front face, and a shelf at the bottom carries the sensor module
// underneath it: component side (pot, chip, header solder joints) up
// against a 6 mm boss around the M3 screw, so nothing but the boss touches,
// sensor side down. Pins point rearward (toward the beam), the TCRT5000
// end forward, ahead of the wheel.
//
// Frame: X along the beam (outboard = +X for the right-hand part), +Y
// forward, +Z up. Origin: the beam's top-front edge at the foot's inboard
// end. `side = "right"` / `"left"` mirrors.
//
// Print: on its side (see print_orient), no supports, no brim.
//
// Render:  openscad -D side=\"right\" -o cliff-mount-right.stl cliff-mount.scad
//          openscad -D side=\"left\"  -o cliff-mount-left.stl  cliff-mount.scad

side = "right";

// ---- Beam (Makeblock 0824 flat; MEASURE) ----------------------------------
beam_top_h   = 51;    // beam top face above the bench, mm (Enoch, 2026-10-03)
beam_depth   = 24;    // top face, front-to-back
hole_pitch   = 16;    // along the beam, within one row
hole_row_y   = -6;    // row centreline from the front edge (front row); back row ~ -18
m4_hole      = 4.5;

// ---- Sensor module (HW-870; MEASURE) ---------------------------------------
pcb_l        = 31.5;  // measured (Enoch, 2026-10-03); along Y when mounted, pins at the rear
pcb_w        = 14;
pcb_hole_d   = 3.2;   // M3 clearance
pcb_hole_in  = 7.5;   // hole centre from the pin-end edge (near edge at 6 mm, Enoch)
boss_h       = 6;     // spacer: clears the pot (~5 mm) and solder tails
boss_d       = 8;
sensor_face_h = 8;    // target: sensor face above the bench (TCRT5000 likes 2-10 mm)
pcb_t        = 1.6;
tcrt_h       = 7;     // TCRT5000 body height below the PCB (sensor side)

// ---- Bracket ----------------------------------------------------------------
foot_l   = hole_pitch + 12;   // along X
foot_w   = 14;                // along Y (sits on the top face)
foot_t   = 4;
plate_t  = 4;                 // drop plate (Y)
plate_w  = foot_l;            // X
shelf_t  = 3;
shelf_y  = pcb_l + 2;         // forward reach of the shelf
// shelf underside height so the sensor face lands at sensor_face_h:
shelf_bot_z = -(beam_top_h - (sensor_face_h + tcrt_h + pcb_t + boss_h));
drop_h   = -shelf_bot_z + shelf_t;   // plate from beam top down to shelf top

$fn = 40;

// ---- v4 (2026-10-04): sensor in front of its wheel ---------------------
// v3 put the sensor 31 mm inboard of the tyre centreline and 54 mm ahead
// of the axle (Enoch's measurements); an angled approach could put the
// tyre over the edge first. v4 moves the TCRT5000 onto the tyre
// centreline (+31 mm outboard) and ~65 mm ahead of the axle. The PCB now
// lies across the robot (along X), pins pointing inboard, so neither the
// board nor its connector reaches back into the tyre.
axle_y      = -22.5;  // axle centre relative to the beam's top-front edge (54 mm lead measured)
tyre_r      = 35;     // ~70 mm wheels (Enoch, 2026-10-04)
tyre_w      = 26;
sensor_x    = plate_w / 2 + 31;  // tyre centreline
sensor_lead = 65;     // TCRT5000 centre ahead of the axle
tcrt_in     = 4;      // TCRT5000 centre from the PCB's sensor-end edge
sensor_y    = axle_y + sensor_lead;
pcb_x1      = sensor_x + tcrt_in;          // sensor-end edge (outboard)
pcb_x0      = pcb_x1 - pcb_l;              // pin-end edge (inboard)
hole_x      = pcb_x0 + pcb_hole_in;
shelf_x1    = pcb_x1 + 3;
shelf_y1    = sensor_y + pcb_w / 2 + 3;
// tyre front at shelf height, plus clearance: no shelf outboard of the
// tyre's inner face behind this line
tyre_in_x   = sensor_x - tyre_w / 2 - 2;
h_shelf     = beam_top_h + shelf_bot_z;    // shelf underside above the bench
tyre_clear_y = axle_y + sqrt(tyre_r * tyre_r - pow(tyre_r - h_shelf, 2)) + 4;

module part() {
  // foot on the beam's top face
  difference() {
    translate([0, -foot_w, 0]) cube([foot_l, foot_w, foot_t]);
    for (i = [0, 1]) translate([6 + i * hole_pitch, hole_row_y, -1]) cylinder(d = m4_hole, h = foot_t + 2);
  }
  // drop plate in front of the beam's front face
  translate([0, 0, shelf_bot_z]) cube([plate_w, plate_t, foot_t - shelf_bot_z]);
  // shelf: an inboard spine (plate width, clear of the tyre) carrying the
  // screw, boss and ribs, plus a narrow arm out over the sensor end of the
  // PCB - nothing else sits in front of the tyre (Enoch's suggestion).
  arm_w = pcb_w + 3;
  difference() {
    union() {
      translate([0, 0, shelf_bot_z]) cube([plate_w, shelf_y1, shelf_t + 1]);
      translate([plate_w - 2, sensor_y - arm_w / 2, shelf_bot_z]) cube([shelf_x1 - plate_w + 2, arm_w, shelf_t + 1]);
    }
    translate([hole_x, sensor_y, shelf_bot_z - 1]) cylinder(d = pcb_hole_d, h = shelf_t + 3);
  }
  // braces: drop plate to shelf top
  for (x = [0, plate_w - 4]) hull() {
    translate([x, plate_t, shelf_bot_z + shelf_t]) cube([4, 0.1, -shelf_bot_z - shelf_t - 2]);
    translate([x, 18, shelf_bot_z + shelf_t]) cube([4, 1, 0.1]);
  }
  // spacer boss under the screw
  difference() {
    translate([hole_x, sensor_y, shelf_bot_z - boss_h]) cylinder(d = boss_d, h = boss_h);
    translate([hole_x, sensor_y, shelf_bot_z - boss_h - 1]) cylinder(d = pcb_hole_d, h = boss_h + 2);
  }
  // side ribs along both long PCB edges (now front/back), from the pin end
  // to 4 mm past the screw, reaching below the board
  rib_l = pcb_hole_in + 4;
  rib_h = boss_h + pcb_t + 2;
  rib_gap = 0.3;
  for (dy = [-(pcb_w / 2 + rib_gap + 1.5), pcb_w / 2 + rib_gap])
    translate([pcb_x0, sensor_y + dy, shelf_bot_z - rib_h]) cube([rib_l, 1.5, rib_h]);
}

module tyre_ghost() {
  translate([sensor_x, axle_y, -beam_top_h + tyre_r]) rotate([0, 90, 0]) cylinder(r = tyre_r, h = tyre_w, center = true);
}

module pcb_ghost() {
  translate([pcb_x0, sensor_y - pcb_w / 2, shelf_bot_z - boss_h - pcb_t]) cube([pcb_l, pcb_w, pcb_t]);
}

// Print orientation: on its SIDE (the L profile extruded upward along X), so
// the foot and shelf are both flat on the bed's plane - no overhangs.
print_orient = true;
module oriented() { if (side == "left") mirror([1, 0, 0]) part(); else part(); }
if (print_orient) { if (side == "left") rotate([0, 90, 0]) oriented(); else rotate([0, -90, 0]) oriented(); }
else { oriented(); %pcb_ghost(); %tyre_ghost(); }
