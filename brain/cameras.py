"""
Still-frame capture from the three cameras.

    bench  - the fixed camera behind the rover's start end (camv3, Thingino):
             BENCH_CAM_HOST, BENCH_CAM_USER (default root), BENCH_CAM_PASS
    front  - the PTZ camera across the bench, facing the rover head-on
             (fishcam, Thingino): FRONT_CAM_HOST, FRONT_CAM_USER, FRONT_CAM_PASS
    rover  - the T-Camera on the rover (ESPHome snapshot server):
             ROVER_CAM_HOST, ROVER_CAM_SNAPSHOT_PORT (default 8081)
"""
import os
import urllib.request

CAMERAS = ("bench", "front", "rover")
THINGINO = {"bench": "BENCH_CAM", "front": "FRONT_CAM"}


def snapshot(camera: str, timeout: float = 15.0) -> bytes:
    if camera in THINGINO:
        pre = THINGINO[camera]
        host = os.environ.get(f"{pre}_HOST")
        pw = os.environ.get(f"{pre}_PASS")
        if not host or not pw:
            raise RuntimeError(f"{pre}_HOST / {pre}_PASS not set")
        user = os.environ.get(f"{pre}_USER", "root")
        url = f"http://{host}/x/image.cgi"
        mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        mgr.add_password(None, url, user, pw)
        opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(mgr))
        with opener.open(url, timeout=timeout) as r:
            return r.read()
    if camera == "rover":
        host = os.environ.get("ROVER_CAM_HOST")
        if not host:
            raise RuntimeError("ROVER_CAM_HOST not set")
        port = os.environ.get("ROVER_CAM_SNAPSHOT_PORT", "8081")
        with urllib.request.urlopen(f"http://{host}:{port}/", timeout=timeout) as r:
            return r.read()
    raise ValueError(f"camera must be one of {CAMERAS}")
