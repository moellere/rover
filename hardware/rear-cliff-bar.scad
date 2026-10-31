// Rear cliff bar: two HW-870 / TCRT5000 cliff sensors behind Grover's
// tracks, so reversing has the same stopping room as driving forward
// (2026-10-31). One printed part: bolts to the tapped M4 holes in the two
// track rails' END faces (Enoch), stands 6 mm off them (the right motor
// plate sticks out ~4 mm past its rail end), steps inboard of the treads,
// runs back, and a crossbar carries the sensors behind each track's
// centreline.
//
// Geometry (Enoch, 10-31): rear axle 8 mm in from the rail ends, rearmost
// tread 30 mm behind them. The front pair sits ~75 mm ahead of the front
// axle, so the rear TCRT5000s sit 75 mm behind the rear axle = 67 mm behind
// the rail ends, ~37 mm past the tread. Faces 13 mm above the bench, like
// the front pair (edge-tested there 10-26).
//
// Sensor module: HW-870 per cliff-mount.scad (31.5 x 14, M3 hole 7.5 mm from
// the pin end, TCRT5000 ~4 mm from the other end, ~7 mm tall below the
// board). Board across the robot, TCRT5000 end OUTBOARD, pins inboard;
// component side up, flat against the frame's underside in a 1 mm locating
// pocket, M3 screw up through the frame; windows let the header joints and
// the pot/chip/LEDs/TCRT5000 leads stand up through it. Nothing hangs below
// the frame but the boards, so it prints flat with no supports.
//
// Frame: +y FORWARD, +x Grover's RIGHT, z up from the bench (right-handed:
// forward x up = right). Origin: centreline, at the rail ends' plane. The
// part is symmetric, so handedness cannot go wrong; the right side is the
// one next to the motor plate.
//
// End holes at 35 and 52 mm above the bench (Enoch, 10-31)
// (Makeblock 0824 on its side, top 56 mm; 36/52 had been assumed). The holes
// are slotted +/-3 mm vertically and +/-0.75 sideways.
//
// Render: openscad -o rear-cliff-bar.stl rear-cliff-bar.scad
// Print:  as rendered (frame flat on the bed, end blocks and ribs up), no
//         supports, no brim. Blue PETG (Grover parts).

// chassis
rail_in_x  = 95 / 2;          // rails' inside faces
rail_w     = 8;               // 0824 on its side
rail_cx    = rail_in_x + rail_w / 2;    // 51.5: end-hole column
hole_z     = [35, 52];        // measured (Enoch, 10-31)
rail_top   = 56;
standoff   = 6;               // clear of the right motor plate (~4 mm proud; 6 per Enoch)
track_cx   = (105 / 2 + 165 / 2) / 2;   // 67.5: track centreline
sensor_y   = -67;             // 75 mm behind the rear axle (8 mm in from the ends)

// sensor module (cliff-mount.scad)
pcb_l = 31.5;  pcb_w = 14;  pcb_t = 1.6;  pcb_hole_in = 7.5;  pcb_hole_d = 3.2;
tcrt_in = 4;   tcrt_h = 7;  
face_z  = 13;

// part
m4_hole  = 4.5;
slot_z   = 3;     // +/- vertical
slot_x   = 0.75;  // +/- sideways (keeps a wall outboard of the hole)
block_x0 = rail_in_x + 0.5;   // end block inboard edge: clear of the motor plate on the rail's inside face
block_x1 = rail_in_x + rail_w;   // stay inside the rail footprint: the sprocket and tread are outboard of it
end_t    = 4;     // end plate behind the standoff
frame_t  = 4;
pocket   = 1;     // PCB locating pocket in the frame's underside
pcb_top  = face_z + tcrt_h + pcb_t;    // 21.6
frame_z0 = pcb_top - pocket;            // frame underside, 20.6 - nothing below it but the boards
arm_x0   = 38;    // arms run back inboard of the treads
arm_x1   = block_x0;
bar_w    = 24;    // crossbar, fore-aft (the PCB windows take 14 of it)
rib_t    = 4;
rib_h    = 12;    // ribs above the frame

pcb_x1 = track_cx + tcrt_in;      // TCRT5000 end (outboard)
pcb_x0 = pcb_x1 - pcb_l;          // pin end (inboard)
hole_x = pcb_x0 + pcb_hole_in;
bar_x  = pcb_x1 + 4;              // crossbar half-length
fit    = 0.4;

$fn = 32;

module half() {   // right half (x > 0); the part is mirrored onto the left
  difference() {
    union() {
      // end block: the standoff plus the end plate, rail-wide, frame to rail top
      translate([block_x0, -standoff - end_t, frame_z0]) cube([block_x1 - block_x0, standoff + end_t, rail_top - frame_z0]);
      // end plate widened inboard behind the standoff, where the arm joins
      translate([arm_x0, -standoff - end_t, frame_z0]) cube([block_x1 - arm_x0, end_t, rail_top - 6 - frame_z0]);
      // arm (frame) and its rib
      translate([arm_x0, sensor_y - bar_w / 2, frame_z0]) cube([arm_x1 - arm_x0, -sensor_y + bar_w / 2 - standoff, frame_t]);
      translate([arm_x0, sensor_y, frame_z0]) cube([rib_t, -sensor_y - standoff - end_t + 0.01, frame_t + rib_h]);
      // crossbar and its rib along the front edge
      translate([0, sensor_y - bar_w / 2, frame_z0]) cube([bar_x, bar_w, frame_t]);
      translate([0, sensor_y + bar_w / 2 - rib_t, frame_z0]) cube([bar_x, rib_t, frame_t + rib_h / 2]);
    }
    // end-hole slots (vertical +/-slot_z, sideways +/-slot_x), through the block
    for (z = hole_z) hull() for (dx = [-slot_x, slot_x], dz = [-slot_z, slot_z])
      translate([rail_cx + dx, 1, z + dz]) rotate([90, 0, 0]) cylinder(d = m4_hole, h = standoff + end_t + 2);
    // PCB pocket in the underside: the board's component side sits flat against its ceiling
    translate([pcb_x0 - fit / 2, sensor_y - (pcb_w + fit) / 2, frame_z0 - 1]) cube([pcb_l + fit, pcb_w + fit, pocket + 1]);
    // windows for what stands up off the board: header joints at the pin end,
    // pot / chip / LEDs / TCRT5000 leads from 12 mm on; a land around the screw
    translate([pcb_x0 - fit / 2, sensor_y - (pcb_w - 2) / 2, frame_z0 - 1]) cube([3.5, pcb_w - 2, frame_t + 2]);
    translate([pcb_x0 + 12, sensor_y - (pcb_w - 2) / 2, frame_z0 - 1]) cube([pcb_l - 12 + fit / 2, pcb_w - 2, frame_t + 2]);
    // M3 sensor screw
    translate([hole_x, sensor_y, frame_z0 - 1]) cylinder(d = pcb_hole_d, h = frame_t + 2);
  }
}

module ghosts() {
  for (s = [-1, 1]) {
    // HW-870 boards
    %translate([s > 0 ? pcb_x0 : -pcb_x1, sensor_y - pcb_w / 2, pcb_top - pcb_t]) cube([pcb_l, pcb_w, pcb_t]);
    // rail ends and the track wrap (rearmost tread 30 mm behind the rail ends)
    %translate([s * rail_cx - rail_w / 2, 0, rail_top - 24]) cube([rail_w, 40, 24]);
    %translate([s * (rail_in_x + rail_w + 1 + 13), 8, 38]) rotate([0, 90, 0]) cylinder(r = 38, h = 26, center = true);   // outboard of the rail
  }
}

half(); mirror([1, 0, 0]) half();
ghosts();
