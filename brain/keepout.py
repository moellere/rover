"""Edge keep-out for the overhead camera (2026-11-02).

The bench's open garage-side edge runs along the TOP of benchcam's frame. On
11-02 a run with the left motor slipping in reverse turned pivots into forward
arcs and left Grover's outer track at that edge, with the overhead logging
"arrived". This guard refuses any brain-commanded move while Grover's marker
is closer than MIN_MM to the edge; a human puts Grover back.

EDGE is the edge line in benchcam pixels, read off the 11-02 frames (the wide
lens bends it); re-read it if the camera is moved.
"""
EDGE = [(300, 372), (520, 322), (700, 300), (965, 265), (1300, 248), (1700, 242), (1900, 246)]
MIN_MM = 130.0   # marker centre to edge: ~80 mm to the outer track, ~50 mm spare
                 # (the taught dock pose sits ~175 mm from the edge)


def edge_y(x: float) -> float:
    pts = EDGE
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def edge_mm(x_px: float, y_px: float, mm_per_px: float) -> float:
    return (y_px - edge_y(x_px)) * mm_per_px


def check(pose) -> str | None:
    """None if Grover may move, else the reason it may not."""
    if pose is None:
        return None
    d = edge_mm(pose.x_px, pose.y_px, pose.mm_per_px or 1.2)
    if d < MIN_MM:
        return f"edge keep-out: marker {d:.0f} mm from the open edge (< {MIN_MM:.0f}) - move Grover by hand"
    return None


def check_move(pose, dist_mm: float) -> str | None:
    """Like check(), but also refuses a straight move whose END lands inside the
    band: dist_mm along the heading (+ forward, - backward). 11-07: a 0.4 s
    undock reverse took Grover from clear to 97 mm from the edge in one pulse,
    so checking only the start was not enough."""
    now = check(pose)
    if now or pose is None:
        return now
    import math
    mpp = pose.mm_per_px or 1.2
    h = math.radians(pose.heading_deg)
    x = pose.x_px + math.cos(h) * dist_mm / mpp
    y = pose.y_px - math.sin(h) * dist_mm / mpp      # image y grows downward
    d = edge_mm(x, y, mpp)
    if d < MIN_MM:
        return (f"edge keep-out: this {abs(dist_mm):.0f} mm {'forward' if dist_mm > 0 else 'backward'} move would end "
                f"{d:.0f} mm from the open edge (< {MIN_MM:.0f}) - move Grover by hand")
    return None
