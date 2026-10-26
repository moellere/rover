// Dock bumper: a clip-on cap for the front edge of each cliff-mount shelf,
// so Grover creeps into the dock until both caps touch the base's back wall
// and the pad bars then sit on the rollers' contact spot (Enoch's idea,
// 2026-10-26). The shelves' front faces are Grover's frontmost points and
// stand 10 mm short of the wall when it charges (Enoch, measured both sides),
// so the cap's face sits `stop` = 10 mm ahead of the shelf. Two caps also
// square Grover against the wall.
//
// It grips the shelf spine of cliff-mount.scad v4 (x 0..plate_w, front edge
// at shelf_y1 = 52.5, 4 mm thick): a jaw over the top (short enough to clear
// the PCB screw head at y 42.5) and a jaw under the bottom - deep only at the
// inboard end, shallow where the sensor PCB sits under the shelf (x >= 17.5,
// its front edge 3 mm behind the shelf's). Handed like the mounts:
// `side = "right"` / `"left"` mirrors.
//
// Frame: as cliff-mount.scad - X along the beam (outboard +X on the right
// part), +Y forward; origin at the shelf's front-bottom inboard corner.
//
// Render:  openscad -o dock-bumper-bar.stl dock-bumper.scad      (v2 bar)
//          openscad -D kind=\"cap\" -D side=\"right\" -o dock-bumper-right.stl dock-bumper.scad
// Print:   profile flat on the bed (print_orient), no supports, no brim.

side = "right";

stop     = 10;     // face ahead of the shelf front (Enoch, 10-26)
shelf_h  = 4.0;    // shelf_t + 1 in cliff-mount.scad
grip     = 0.1;    // per side: snug press fit in PETG
width    = 28;     // the shelf spine (plate_w)
jaw_t    = 2;
top_jaw  = 6;      // clears the M3 screw head (shelf front 52.5, screw at 42.5)
low_deep = 8;      // under the inboard end, x < pcb_free
low_flat = 1.0;    // under the PCB end: the PCB ribs end 1.2 mm behind the shelf front
pcb_free = 15;     // the PCB starts at x 17.5
chamfer  = 1.5;

gap = shelf_h + 2 * grip;

module profile_block(x0, x1, low) {
  translate([x0, 0, 0]) {
    // bumper block ahead of the shelf face, full height of jaws + gap
    hull() {
      translate([0, 0, -jaw_t]) cube([x1 - x0, 0.01, gap + 2 * jaw_t]);
      translate([0, stop - chamfer, -jaw_t]) cube([x1 - x0, 0.01, gap + 2 * jaw_t]);
      translate([0, stop, -jaw_t + chamfer]) cube([x1 - x0, 0.01, gap + 2 * jaw_t - 2 * chamfer]);
    }
    // top jaw, reaching back over the shelf
    translate([0, -top_jaw, gap]) cube([x1 - x0, top_jaw + 0.01, jaw_t]);
    // bottom jaw
    translate([0, -low, -jaw_t]) cube([x1 - x0, low + 0.01, jaw_t]);
  }
}

module part() {
  profile_block(0, pcb_free, low_deep);
  profile_block(pcb_free, width, low_flat);
}

// v2 (Enoch, 10-26): ONE bar clipped to both shelves - both stop faces in
// one plane squares Grover better than two caps, and it can't lose a half.
// The shelves' inboard ends are `shelf_gap` apart (Enoch: 20 mm); the bridge
// across it is only the bumper block, in front of the shelves, clear of the
// TFMini wires that loop down through the gap. Origin: the bar's centre.
shelf_gap = 20;
module bar() {
  for (s = [1, -1]) mirror([s < 0 ? 1 : 0, 0, 0]) translate([shelf_gap / 2, 0, 0]) part();
  hull() {   // bridge: the bumper block between the two clips
    translate([-shelf_gap / 2 - 0.01, 0, -jaw_t]) cube([shelf_gap + 0.02, 0.01, gap + 2 * jaw_t]);
    translate([-shelf_gap / 2 - 0.01, stop - chamfer, -jaw_t]) cube([shelf_gap + 0.02, 0.01, gap + 2 * jaw_t]);
    translate([-shelf_gap / 2 - 0.01, stop, -jaw_t + chamfer]) cube([shelf_gap + 0.02, 0.01, gap + 2 * jaw_t - 2 * chamfer]);
  }
}

kind = "bar";          // "bar" (v2) or "cap" (v1, with `side`)
print_orient = true;
module oriented() { if (side == "left") mirror([1, 0, 0]) part(); else part(); }
if (kind == "bar") {
  // print on its bumper face: the jaws rise straight up from the block, no overhangs
  if (print_orient) translate([0, 0, stop]) rotate([-90, 0, 0]) bar(); else bar();
} else {
  // a single cap stands on its inboard (x = 0) end: the profile lies flat on the bed
  if (print_orient) { if (side == "left") rotate([0, 90, 0]) oriented(); else rotate([0, -90, 0]) oriented(); }
  else oriented();
}
