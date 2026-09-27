// Camera mount: holds a TTGO T-Camera (ESP32-WROVER-B, OV2640 V1.7) upright on
// the rover's Makeblock plate, camera/PIR/OLED facing forward, tilted down.
//
// Design: a raised cradle on a pedestal. Two side rails grip the PCB's long
// edges in slots; the front is fully open (nothing in front of the lens, PIR,
// or OLED). The board's BOTTOM edge carries the micro-USB port and the 5-pin
// connector, so the cradle floats `usb_clear` mm above the base with an open
// gap underneath: the board rests on two small corner tabs, the USB plug hangs
// through the gap, and the cable exits rearward through a window in the
// pedestal. The base bolts to the Makeblock plate with M4 hardware on the
// plate's 8mm hole grid.
//
// Render:  openscad -o camera-mount.stl camera-mount.scad
// Print:   base down, no brim, tree supports on auto (see hardware/README.md)
//
// !! PLACEHOLDER DIMENSIONS - the pcb_* and usb_* values are estimates and
// !! MUST be replaced with caliper measurements of the real board first.

// ---- Board (MEASURE THESE) --------------------------------------------------
pcb_w     = 28.0;   // PCB width  (bottom/top edge), mm      <- measure
pcb_l     = 62.0;   // PCB length (side edge, bottom->top), mm <- measure
pcb_t     = 1.6;    // PCB thickness, mm                     <- measure
comp_back = 4.0;    // tallest component on the BACK face, mm <- measure
usb_x     = 0.0;    // micro-USB centre offset from the board's centreline
                    // along the bottom edge (+ = right, viewed from the
                    // lens side), mm                        <- measure
usb_plug_w = 12.0;  // width of the micro-USB PLUG overmold (not the socket)
usb_plug_t = 8.0;   // thickness of the plug overmold (front-to-back)
usb_clear  = 16.0;  // gap under the board for plug body + cable bend

// ---- Mount geometry --------------------------------------------------------
wall      = 3.0;    // rail/backplate/pedestal thickness
clear     = 0.3;    // slot clearance around the PCB (PETG shrinks a little)
rail_d    = 3.0;    // how deep each rail overlaps the PCB edge
lip       = 2.0;    // front lip height that stops the board sliding forward
tab_w     = 5.0;    // width of the two bottom corner tabs the board rests on
tilt      = 10;     // degrees the camera looks DOWN from horizontal
base_l    = 44;     // base plate length (along the rover's travel axis)
base_t    = 3.0;    // base plate thickness

inner_w  = pcb_w + 2*clear;
inner_t  = pcb_t + 2*clear;
outer_w  = inner_w + 2*wall;
depth    = comp_back + wall + inner_t + lip;   // cradle front-to-back
base_w   = outer_w + 8;

// ---- Makeblock plate interface ---------------------------------------------
mb_pitch  = 8;      // Makeblock hole grid, mm
m4_hole   = 4.4;    // M4 clearance
slot_len  = 8;      // slots let the mount sit on either 8mm or 16mm centres

$fn = 48;

module base() {
  difference() {
    linear_extrude(base_t)
      offset(r=3) offset(delta=-3) square([base_w, base_l], center=true);
    for (x = [-mb_pitch, mb_pitch])
      hull() for (y = [-slot_len/2, slot_len/2])
        translate([x, y, -1]) cylinder(d=m4_hole, h=base_t+2);
  }
}

// Built "flat": board face toward +Z, board length along +Y, bottom edge at
// y = 0. The pedestal extends below y = 0 down to y = -usb_clear.
module cradle_flat() {
  z0 = -(comp_back + wall);            // back face of the back plate
  h  = pcb_l;
  difference() {
    union() {
      // back plate, running from the pedestal foot up to the top of the board
      translate([-outer_w/2, -usb_clear, z0]) cube([outer_w, usb_clear + h, wall]);
      // side rails (full board length) and their pedestal legs below
      for (s = [-1, 1])
        translate([s*(inner_w/2) - (s<0 ? wall : 0), -usb_clear, z0])
          cube([wall, usb_clear + h, depth]);
      // front lips over the front face along each edge
      for (s = [-1, 1])
        translate([s*(inner_w/2) - (s<0 ? rail_d : 0), 0, inner_t])
          cube([rail_d, h, lip]);
      // two bottom corner tabs the board's bottom edge rests on
      for (s = [-1, 1])
        translate([s*(inner_w/2) - (s<0 ? tab_w : 0), -wall, z0])
          cube([tab_w, wall, depth]);
    }
    // the USB plug hangs through the gap between the tabs; make sure the gap
    // is at least the plug width, centred on the port
    translate([usb_x - usb_plug_w/2, -usb_clear - 1, z0 - 1])
      cube([usb_plug_w, usb_clear + 2, depth + 2]);
    // cable exit window through the back plate, below the board
    translate([-outer_w/2 + wall, -usb_clear + wall, z0 - 1])
      cube([outer_w - 2*wall, usb_clear - 2*wall, wall + 2]);
  }
}

module mount() {
  base();
  // Stand the cradle up: 90 deg about X points the board face along -Y
  // (forward) with the board length up +Z; more than 90 leans the top
  // forward so the lens looks DOWN by `tilt`. The pedestal foot (y = -usb_clear
  // in flat coords) lands on the base.
  translate([0, 0, base_t])
    rotate([90 + tilt, 0, 0])
      translate([0, usb_clear, 0])
        cradle_flat();
}

mount();
