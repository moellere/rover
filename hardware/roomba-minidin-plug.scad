// 7-pin mini-DIN plug body for a Roomba Open Interface port (issue #1).
// SHELVED 2026-09-28: the Roomba turned out to be gone. Test print #1 findings,
// for whoever revives this: (a) the key must be an INSET groove in the insert,
// not a protruding rib - the socket has a rib, the plug has the slot;
// (b) the wire holes were too small - raise wire_d/ins_d. Both are fixed below.
// Holds seven lengths of solid-core wire at the socket's pin positions, so the
// wires themselves are the contacts (a well-worn Roomba hack, made repeatable).
//
// Geometry: pin positions traced from the mini-DIN-7 diagram scaled to the
// standard 9.5 mm face; the fit-critical values (shell clearance, key size,
// hole size) are parameters to tune with a test print - iterate, don't guess.
//
// Build: strip ~12 mm of solid-core wire, push it through from the back until
// it protrudes `pin_proud` mm past the face, hot-glue the back. The face view
// below is the PLUG face (mirror of the socket face).
//
// Render: openscad -o roomba-minidin-plug.stl roomba-minidin-plug.scad

// ---- fit parameters (tune with a test print) ------------------------------
shell_d    = 9.2;    // insert OD; socket nominal 9.5 mm minus clearance
insert_len = 8.0;    // how far the insert goes into the socket
key_w      = 1.6;    // top key GROOVE width (socket rib goes in it)
key_h      = 0.8;    // key groove depth
wire_d     = 1.0;    // hole for the bare conductor (0.75 was too tight for 22 AWG after printing)
ins_d      = 2.2;    // hole for the insulated wire behind the insert (1.7 was too tight)
pin_proud  = 6.0;    // how far bare wire should stick out of the face (for info)

// ---- grip --------------------------------------------------------------
grip_d     = 15.0;
grip_len   = 12.0;

// Pin centres, mm, socket-face coordinates (x right, y up). Mirrored in X for
// the plug face. Labels: T = top row, M = middle pair, B = bottom pair.
pins = [ [-2.20,  1.82], [0, 1.82], [ 2.20, 1.82],      // T1 T2 T3
         [-2.75, -0.37],            [ 2.75, -0.37],     // M1    M2
         [-1.12, -2.55],            [ 1.12, -2.55] ];   // B1    B2

$fn = 64;

module body() {
  union() {
    // insert (face at z = 0, going +z into the socket... modelled face-down
    // so it prints face-up: insert on top of the grip)
    translate([0, 0, grip_len]) cylinder(d = shell_d, h = insert_len);
    // grip with a flat on top so "up" is obvious by touch
    difference() {
      cylinder(d = grip_d, h = grip_len);
      translate([-grip_d, grip_d/2 - 1.2, -1]) cube([2*grip_d, grip_d, grip_len + 2]);
    }
  }
}

module holes() {
  for (p = pins) {
    x = -p[0]; y = p[1];                       // mirror socket face -> plug face
    translate([x, y, -1]) cylinder(d = ins_d, h = grip_len - 2 + 1);   // insulated part
    translate([x, y, grip_len - 2]) cylinder(d = wire_d, h = insert_len + 3); // bare conductor
    // cone transition so the insulation seats against a shoulder
    translate([x, y, grip_len - 2]) cylinder(d1 = ins_d, d2 = wire_d, h = 0.8);
  }
}

module key_groove() {  // inset groove along the top of the insert
  translate([-key_w/2, shell_d/2 - key_h, grip_len - 1]) cube([key_w, key_h + 1, insert_len + 2]);
}

difference() { body(); holes(); key_groove(); }
