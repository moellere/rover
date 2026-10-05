"""
Overhead localisation: where is Grover on the bench, and which way is it
pointing - from the overhead bench camera (fishcam, looking straight down).

Grover carries a small ArUco marker taped flat on top (id 2, 60 mm,
`hardware/markers/aruco_4x4_50_id2_60mm.png`) with the printed "FRONT" edge
toward the rover's nose. In the marker's own frame OpenCV returns corners
top-left, top-right, bottom-right, bottom-left, so the "up" vector
(bottom-edge midpoint -> top-edge midpoint) is the rover's forward
direction.

Angles are in the image plane: 0 deg = image right, 90 deg = image up
(counter-clockwise positive). With fishcam's current mount the homing
marker end of the bench is image-left (180 deg) and the open garage-side
edge is image-up (90 deg).

Scale: mm per pixel near the marker, from its known printed size. The lens
is wide, so treat positions far from the image centre as approximate.
"""
from dataclasses import dataclass, asdict
from typing import Optional

import cv2
import numpy as np

from brain.markers import _DETECTOR, _CLAHE

ROVER_TOP_ID = 2
TOP_MARKER_MM = {2: 60.0, 0: 80.0, 1: 160.0}


@dataclass
class Pose:
    id: int
    x_px: float
    y_px: float
    heading_deg: float          # rover/marker forward, image frame, CCW from image-right
    mm_per_px: Optional[float]  # local scale from the marker's printed size
    side_px: float


def _detect(gray):
    corners, ids, _ = _DETECTOR.detectMarkers(gray)
    if ids is None:
        corners, ids, _ = _DETECTOR.detectMarkers(_CLAHE.apply(gray))
    return corners, ids


def poses(jpeg: bytes) -> list[Pose]:
    img = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("could not decode image")
    corners, ids = _detect(img)
    out: list[Pose] = []
    if ids is None:
        return out
    for quad, mid in zip(corners, ids.flatten()):
        tl, tr, br, bl = quad.reshape(4, 2)
        c = (tl + tr + br + bl) / 4
        up = (tl + tr) / 2 - (bl + br) / 2
        heading = float(np.degrees(np.arctan2(-up[1], up[0])))   # image y grows downward
        side = float(np.mean([np.linalg.norm(a - b) for a, b in ((tl, tr), (tr, br), (br, bl), (bl, tl))]))
        mm = TOP_MARKER_MM.get(int(mid))
        out.append(Pose(int(mid), float(c[0]), float(c[1]), round(heading % 360, 1),
                        (mm / side) if mm and side > 0 else None, round(side, 1)))
    return out


def heading_change(before: float, after: float) -> float:
    """Signed smallest rotation from `before` to `after`, degrees (CCW +)."""
    return (after - before + 180) % 360 - 180


def poses_as_dicts(jpeg: bytes) -> list[dict]:
    return [asdict(p) for p in poses(jpeg)]
