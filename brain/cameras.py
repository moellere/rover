"""
Still-frame capture from the three cameras.

    bench  - the fixed camera behind the rover's start end (camv3, Thingino):
             BENCH_CAM_HOST, BENCH_CAM_USER (default root), BENCH_CAM_PASS
    front  - the PTZ camera across the bench, facing the rover head-on
             (fishcam, Thingino): FRONT_CAM_HOST, FRONT_CAM_USER, FRONT_CAM_PASS
    rover  - the T-Camera on the rover (ESPHome snapshot server):
             ROVER_CAM_HOST, ROVER_CAM_SNAPSHOT_PORT (default 8081)
    eufy   - the camera on the Eufy's lid: EUFY_CAM_KIND = esphome (a
             T-Camera, blackcam; EUFY_CAM_HOST, snapshot port 8081) or
             thingino (camv3; EUFY_CAM_HOST, EUFY_CAM_USER, EUFY_CAM_PASS)

(2026-10-05: `bench` is fishcam, overhead; `front` is camv3 until it moves
to the Eufy - names are just env prefixes, the hosts live in the env file.)
"""
import os
import urllib.request

CAMERAS = ("bench", "front", "rover", "eufy")
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
    if camera == "eufy":
        kind = os.environ.get("EUFY_CAM_KIND", "esphome")
        host = os.environ.get("EUFY_CAM_HOST")
        if not host:
            raise RuntimeError("EUFY_CAM_HOST not set")
        if kind == "thingino":
            url = f"http://{host}/x/image.cgi"
            mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            mgr.add_password(None, url, os.environ.get("EUFY_CAM_USER", "root"), os.environ.get("EUFY_CAM_PASS", ""))
            with urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(mgr)).open(url, timeout=timeout) as r:
                return r.read()
        with urllib.request.urlopen(f"http://{host}:8081/", timeout=timeout) as r:
            return r.read()
    raise ValueError(f"camera must be one of {CAMERAS}")
