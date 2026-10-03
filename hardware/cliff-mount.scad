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

module part() {
  // foot on the beam's top face (y from -foot_w to 0, z 0..foot_t)
  difference() {
    translate([0, -foot_w, 0]) cube([foot_l, foot_w, foot_t]);
    for (i = [0, 1]) translate([6 + i * hole_pitch, hole_row_y, -1]) cylinder(d = m4_hole, h = foot_t + 2);
  }
  // drop plate in front of the beam's front face
  translate([0, 0, shelf_bot_z]) cube([plate_w, plate_t, foot_t - shelf_bot_z]);
  // shelf
  difference() {
    translate([0, 0, shelf_bot_z]) cube([plate_w, shelf_y + plate_t, shelf_t]);
    translate([plate_w / 2, plate_t + pcb_hole_in, shelf_bot_z - 1]) cylinder(d = pcb_hole_d, h = shelf_t + 2);
  }
  // boss under the shelf (the spacer) - M3 through it into the PCB
  difference() {
    translate([plate_w / 2, plate_t + pcb_hole_in, shelf_bot_z - boss_h]) cylinder(d = boss_d, h = boss_h);
    translate([plate_w / 2, plate_t + pcb_hole_in, shelf_bot_z - boss_h - 1]) cylinder(d = pcb_hole_d, h = boss_h + 2);
  }
  // anti-rotation rib: a thin wall the PCB's rear (pin) edge rests against
  translate([plate_w / 2 - pcb_w / 2 - 1.5, plate_t, shelf_bot_z - boss_h]) cube([1.5, 6, boss_h]);
  translate([plate_w / 2 + pcb_w / 2, plate_t, shelf_bot_z - boss_h]) cube([1.5, 6, boss_h]);
}

module pcb_ghost() {
  translate([plate_w / 2 - pcb_w / 2, plate_t, shelf_bot_z - boss_h - pcb_t]) cube([pcb_w, pcb_l, pcb_t]);
}

// Print orientation: on its SIDE (the L profile extruded upward along X), so
// the foot and shelf are both flat on the bed's plane - no overhangs.
print_orient = true;
module oriented() { if (side == "left") mirror([1, 0, 0]) part(); else part(); }
if (print_orient) { if (side == "left") rotate([0, 90, 0]) oriented(); else rotate([0, -90, 0]) oriented(); }
else { oriented(); %pcb_ghost(); }
