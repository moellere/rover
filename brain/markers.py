"""
ArUco marker detection for visual homing.

Finds 4x4_50 markers in a JPEG and reports, per marker: id, pixel centre,
apparent side length, and the horizontal bearing from the image centre in
degrees (needs the camera's horizontal field of view). Distance is estimated
from apparent size once the focal length is known - see `estimate_distance`.

Calibration (Tier 1.3 on the roadmap): photograph the printed marker at a
measured distance D with the mounted camera, read `side_px`, then
    focal_px = side_px * D / MARKER_MM
and put that number in ROVER_CAM_FOCAL_PX. Until then, distance is None.
"""
import os
from dataclasses import dataclass, asdict
from typing import Optional

import cv2
import numpy as np

MARKER_MM = float(os.environ.get("ROVER_MARKER_MM", "80"))   # default size
MARKER_SIZES_MM = {0: 80.0, 1: 160.0}                             # printed pages in hardware/markers/
CAM_HFOV_DEG = float(os.environ.get("ROVER_CAM_HFOV_DEG", "66"))  # OV2640 typical

# Per-camera focal length in pixels, from a marker of known size at a known
# distance: focal_px = side_px * distance_mm / MARKER_MM.
#   BENCH_CAM_FOCAL_PX  - the fixed workbench camera
#   FRONT_CAM_FOCAL_PX  - the head-on camera across the bench
#   ROVER_CAM_FOCAL_PX  - the T-Camera on the rover
def focal_px(camera: str) -> Optional[float]:
    v = os.environ.get({"bench": "BENCH_CAM_FOCAL_PX", "front": "FRONT_CAM_FOCAL_PX", "rover": "ROVER_CAM_FOCAL_PX"}.get(camera, ""))
    return float(v) if v else None

_DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
_PARAMS = cv2.aruco.DetectorParameters()
_DETECTOR = cv2.aruco.ArucoDetector(_DICT, _PARAMS)


@dataclass
class Marker:
    id: int
    cx: float
    cy: float
    side_px: float
    bearing_deg: float          # + = marker is to the right of centre
    distance_mm: Optional[float]
    image_w: int
    image_h: int


def estimate_distance(side_px: float, camera: str = "rover", marker_id: int = 0) -> Optional[float]:
    f = focal_px(camera)
    if not f or side_px <= 0:
        return None
    return f * MARKER_SIZES_MM.get(marker_id, MARKER_MM) / side_px


def find_markers(jpeg: bytes, camera: str = "rover") -> list[Marker]:
    arr = np.frombuffer(jpeg, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("could not decode image")
    h, w = img.shape[:2]
    corners, ids, _ = _DETECTOR.detectMarkers(img)
    out: list[Marker] = []
    if ids is None:
        return out
    for quad, mid in zip(corners, ids.flatten()):
        pts = quad.reshape(4, 2)
        cx, cy = pts.mean(axis=0)
        # apparent side = mean of the four edge lengths
        side = float(np.mean([np.linalg.norm(pts[i] - pts[(i + 1) % 4]) for i in range(4)]))
        # small-angle-free bearing: map pixel offset through the pinhole model
        half_w = w / 2.0
        f_px = focal_px(camera) or (half_w / np.tan(np.radians(CAM_HFOV_DEG / 2)))
        bearing = float(np.degrees(np.arctan2(cx - half_w, f_px)))
        out.append(Marker(int(mid), float(cx), float(cy), side, bearing,
                          estimate_distance(side, camera, int(mid)), w, h))
    return out


def markers_as_dicts(jpeg: bytes, camera: str = "rover") -> list[dict]:
    return [asdict(m) for m in find_markers(jpeg, camera)]
