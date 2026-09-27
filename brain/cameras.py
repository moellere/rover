"""
Still-frame capture from the two cameras.

    bench  - the fixed ONVIF camera over the workbench (Thingino firmware):
             BENCH_CAM_HOST, BENCH_CAM_USER (default root), BENCH_CAM_PASS
    rover  - the T-Camera on the rover (ESPHome snapshot server):
             ROVER_CAM_HOST, ROVER_CAM_SNAPSHOT_PORT (default 8081)
"""
import os
import urllib.request

CAMERAS = ("bench", "rover")


def snapshot(camera: str, timeout: float = 15.0) -> bytes:
    if camera == "bench":
        host = os.environ.get("BENCH_CAM_HOST")
        pw = os.environ.get("BENCH_CAM_PASS")
        if not host or not pw:
            raise RuntimeError("BENCH_CAM_HOST / BENCH_CAM_PASS not set")
        user = os.environ.get("BENCH_CAM_USER", "root")
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
