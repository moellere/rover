// Marker bracket (2026-11-01, Enoch's design): a C-shaped bracket (side view)
// that carries marker cap v1 (marker-cap.scad, ArUco id 2) above the spine
// deck now that battery cradle v3 - which the cap clipped onto - is gone.
//
//   - Feet: two bolt loops on the REAR post bolts (+/-32, -48), thin enough
//     that the rear-left one slides under the FNK0101's edge (the board
//     stands on 5 mm standoffs) with the button head on top.
//   - Spine: two legs just behind the loops, outboard of the posts, joined
//     at the top - the FNK0101's barrel-jack plug (sticking out rearward at
//     x ~ -19) passes between them.
//   - Top arm: a cross beam on the legs and a tongue forward to a 40 mm pad;
//     marker cap v1's plate rests on the pad and is screwed down (two M3
//     self-tappers into pilots here, through holes Enoch drills in the cap).
//     The pad sits high enough that the cap's 13 mm skirts clear the wiring
//     (pressed to 45 mm) - 13 mm lower if the skirts are trimmed off.
//
// Frame: +y FORWARD, +x Grover's RIGHT, z up from the top plate's top face
// (right-handed; checked per CLAUDE.md's handedness rule). Origin: centre of
// the deck posts (top-plate.scad).
//
// CONFIRM with Enoch before slicing: loop thickness vs the gap under the
// FNK0101 at the rear-left bolt; thread left in the posts with the loops
// under the bolt heads; the space behind the plate's rear edge; arm height.
//
// Render: openscad -o marker-bracket.stl marker-bracket.scad
// Print:  on its back (the legs' rear faces down), no supports, no brim.
//         Blue PETG (Grover parts).

post_x = 32;  post_y = -48;     // rear posts (top-plate.scad)
plate_rear = -53;               // top plate's rear edge
m4_hole = 4.5;  slot = 1.5;     // fore-aft slot as in the top plate

loop_t  = 2.5;                  // under the FNK0101: 5 mm gap - head (~2.2) leaves ~0.3
loop_d  = 11;
leg_w   = 8;                    // across (x)
leg_t   = 5;                    // fore-aft
leg_x   = post_x + 2;           // leg centre, just outboard of the post
leg_y1  = post_y - loop_d / 2 - 0.5;   // leg front face, behind the bolt head
leg_y0  = leg_y1 - leg_t;

skirts  = true;                 // cap v1 keeps its 13 mm skirts (false if Enoch trims them off)
wire_z  = 45;                   // tallest wiring, pressed down (Enoch)
skirt_h = 13 + 2.4;             // cap v1: skirt bottoms this far below its top face
arm_t   = 4;
pad_top = skirts ? wire_z + skirt_h - 2.4 : wire_z + 3;   // the cap's plate rests here
clear_z = pad_top - arm_t;      // cross beam / tongue underside
pad     = 40;                   // square screw pad
pad_y   = -20;                  // pad (and marker) centre: cap v1's skirts (y +/-28 about it)
                                // then clear the legs and cross beam behind
tongue_w = 24;
screw_dx = 24;                  // two M3 self-tappers, across; Enoch drills the cap to match
m3_pilot = 2.6;
top_z   = pad_top;

$fn = 32;

module loop(sx) {
  difference() {
    hull() {
      translate([sx * leg_x - leg_w / 2, leg_y1 - 0.01, 0]) cube([leg_w, 0.01, loop_t]);
      hull() for (dy = [-slot, slot]) translate([sx * post_x, post_y + dy, 0]) cylinder(d = loop_d, h = loop_t);
    }
    hull() for (dy = [-slot, slot]) translate([sx * post_x, post_y + dy, -1]) cylinder(d = m4_hole, h = loop_t + 2);
  }
}

module leg(sx) {
  translate([sx * leg_x - leg_w / 2, leg_y0, 0]) cube([leg_w, leg_t, clear_z + arm_t]);
  // gusset: leg into loop
  hull() {
    translate([sx * leg_x - 1.5, leg_y1 - 0.01, 0]) cube([3, 0.01, 14]);
    translate([sx * leg_x - 1.5, leg_y1, 0]) cube([3, 5, loop_t]);
  }
}

module arm() {
  // cross beam over the legs, a tongue forward along the centreline, the pad
  translate([-(leg_x + leg_w / 2), leg_y0, clear_z]) cube([2 * (leg_x + leg_w / 2), leg_t, arm_t]);
  difference() {
    union() {
      translate([-tongue_w / 2, leg_y0, clear_z]) cube([tongue_w, pad_y - leg_y0, arm_t]);
      translate([-pad / 2, pad_y - pad / 2, clear_z]) cube([pad, pad, arm_t]);
      // stiffening rib under the tongue
      translate([-1.5, leg_y0, clear_z - 6]) cube([3, pad_y + pad / 2 - leg_y0 - 4, 6]);
    }
    for (sx = [-1, 1]) translate([sx * screw_dx / 2, pad_y, clear_z - 7]) cylinder(d = m3_pilot, h = arm_t + 8);
  }
}

module bracket() {
  for (sx = [-1, 1]) { loop(sx); leg(sx); }
  arm();
}

bracket();
// ghosts: FNK0101 rear edge region, posts, cap v1 plate
%translate([-75.1, -46.1, 5]) cube([87.6, 10, 21.6]);
%for (sx = [-1, 1]) translate([sx * post_x, post_y, -30]) cylinder(d = 8, h = 30);
%translate([-39, pad_y - 39, top_z]) cube([78, 78, 2.4]);
%for (sx = [-1, 1]) translate([sx * 34.3 - 0.8, pad_y - 28, top_z - 13]) cube([1.6, 56, 13]);   // cap v1 skirts

echo(str("marker bracket: pad top ", pad_top, " mm above the plate, skirt bottoms at ", pad_top + 2.4 - skirt_h,
         "; marker centre y = ", pad_y, " (", pad_y - post_y, " ahead of the rear posts)"));
