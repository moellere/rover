#!/usr/bin/env python3
"""
Grab a still JPEG snapshot from the workbench ONVIF camera (Thingino firmware).

Gotchas documented here because they cost real debugging time:
  - `/x/preview.cgi` returns the HTML viewer page, not an image.
    The actual snapshot endpoint is `/x/image.cgi`.
  - Thingino's default/expected login is username `root` - not whatever
    username you may have saved alongside the password. If you get a 401
    with a body explaining "the username is root", that's why.

Usage:
    CAMERA_HOST=<ip-or-hostname> CAMERA_PASS=<password> \\
        python3 camera_snapshot.py out.jpg
    [CAMERA_USER defaults to "root"]
"""
import os
import sys
import urllib.request

HOST = os.environ.get("CAMERA_HOST")
USER = os.environ.get("CAMERA_USER", "root")
PASSWORD = os.environ.get("CAMERA_PASS")


def main():
    if not HOST or not PASSWORD:
        raise SystemExit("Set CAMERA_HOST and CAMERA_PASS env vars.")
    if len(sys.argv) < 2:
        raise SystemExit("Usage: camera_snapshot.py <output.jpg>")
    out_path = sys.argv[1]

    url = f"http://{HOST}/x/image.cgi"
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, url, USER, PASSWORD)
    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(handler)

    with opener.open(url, timeout=10) as resp:
        data = resp.read()

    with open(out_path, "wb") as f:
        f.write(data)
    print(f"Saved {len(data)} bytes to {out_path}")


if __name__ == "__main__":
    main()
