// Camera mount: holds a TTGO T-Camera (ESP32-WROVER-B, OV2640 V1.7) upright on
// the rover's Makeblock plate, camera/PIR/OLED facing forward.
//
// Design: a cradle. Two side rails grip the PCB's long edges in slots; the front
// is fully open (nothing in front of the lens, PIR, or OLED); the back is a
// plate with a window for the micro-USB lead and the buttons. The base bolts
// to the Makeblock plate with M4 hardware on the plate's 8mm hole grid.
//
// Render:  openscad -o camera-mount.stl camera-mount.scad
// Preview: openscad camera-mount.scad
//
// !! PLACEHOLDER DIMENSIONS - the pcb_* values below are estimates and MUST be
// !! replaced with caliper measurements of the actual board before printing.
// !! Everything else derives from them.

// ---- Board (MEASURE THESE) --------------------------------------------------
pcb_w     = 28.0;   // PCB width  (short edge), mm  <- measure
pcb_l     = 62.0;   // PCB length (long edge),  mm  <- measure
pcb_t     = 1.6;    // PCB thickness, mm            <- measure
comp_back = 4.0;    // tallest component height on the BACK face (buttons,
                    // battery connector), mm       <- measure
usb_from_bottom = 12.0; // micro-USB centre height above the board's bottom
                        // edge when standing upright, mm  <- measure
usb_edge  = "right";    // which long edge the micro-USB sits on: "left"/"right"
                        // when viewed from the FRONT (lens side)  <- confirm

// ---- Mount geometry --------------------------------------------------------
wall      = 3.0;    // rail/backplate thickness (62mm lever on a moving rover)
clear     = 0.3;    // slot clearance around the PCB (PETG shrinks a little)
rail_d    = 3.0;    // how deep each rail overlaps the PCB edge
lip       = 2.0;    // front lip height that stops the board sliding forward
tilt      = 10;     // degrees the camera looks DOWN from horizontal
                    // (0 = straight ahead; ~10 sees the bench surface ahead)
base_l    = 40;     // base plate length (along the rover's travel axis)
base_w    = pcb_w + 2*wall + 2*rail_d + 8;  // base plate width
base_t    = 3.0;    // base plate thickness

// ---- Makeblock plate interface ---------------------------------------------
mb_pitch  = 8;      // Makeblock hole grid, mm
m4_hole   = 4.4;    // M4 clearance
slot_len  = 8;      // slots let the mount sit on either 8mm or 16mm centres

$fn = 48;

module base() {
  difference() {
    // rounded rectangle base
    linear_extrude(base_t)
      offset(r=3) offset(delta=-3) square([base_w, base_l], center=true);
    // two M4 slots, 16mm apart across the width, centred
    for (x = [-mb_pitch, mb_pitch])
      hull() for (y = [-slot_len/2, slot_len/2])
        translate([x, y, -1]) cylinder(d=m4_hole, h=base_t+2);
  }
}

// The cradle is built lying "flat" with the board face pointing +Z, then stood
// up and tilted so the lens looks along -Y (forward) with a downward tilt.
module cradle_flat() {
  inner_w = pcb_w + 2*clear;
  inner_t = pcb_t + 2*clear;
  outer_w = inner_w + 2*wall;
  h       = pcb_l;            // rails run the full board length
  difference() {
    union() {
      // back plate
      translate([-outer_w/2, 0, -(comp_back + wall)])
        cube([outer_w, h, wall]);
      // two side rails
      for (s = [-1, 1])
        translate([s*(inner_w/2) - (s<0 ? wall : 0), 0, -(comp_back + wall)])
          cube([wall, h, comp_back + wall + inner_t + wall]);
      // front lips (small tabs over the front face along each edge)
      for (s = [-1, 1])
        translate([s*(inner_w/2) - (s<0 ? rail_d : 0), 0, inner_t])
          cube([rail_d, h, lip]);
      // bottom end stop
      translate([-outer_w/2, -wall, -(comp_back + wall)])
        cube([outer_w, wall, comp_back + wall + inner_t + lip]);
    }
    // window in the back plate for the USB lead and buttons
    translate([-outer_w/2 + wall + 1, usb_from_bottom - 6, -(comp_back + wall) - 1])
      cube([outer_w - 2*wall - 2, 12, wall + 2]);
    // relief so the side rails don't cover the USB port itself
    ux = (usb_edge == "right") ? inner_w/2 : -inner_w/2 - wall;
    translate([ux, usb_from_bottom - 6, -(comp_back + wall) - 1])
      cube([wall, 12, comp_back + wall + inner_t + lip + 2]);
  }
}

module mount() {
  base();
  // Stand the cradle up: a 90 deg rotation about X turns the board's +Z face
  // to look along -Y (forward) with its length running up +Z. Rotating
  // *more* than 90 leans the top forward, so the lens looks DOWN by `tilt`.
  // (Rotating less than 90 leans it back and looks up - the wrong way; the
  // first render caught exactly that.)
  translate([0, 0, base_t])
    rotate([90 + tilt, 0, 0])
      cradle_flat();
}

mount();
