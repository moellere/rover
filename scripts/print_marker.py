#!/usr/bin/env python3
"""
Print a marker page from hardware/markers/ on a network inkjet over IPP,
at exactly 100 % (no fit-to-page), so the ArUco square comes out the size
the brain assumes.

The page PNGs are 2550x3300 (US Letter at 300 DPI). The printer here is an
AirPrint-class inkjet that takes JPEG but not PDF, so the page is re-encoded
as a JPEG whose JFIF header says 300 x 300 dpi and submitted with
print-scaling=none on Letter. Check the 100 mm scale bar with a ruler on
the first print.

Needs `ipptool` (Debian/Ubuntu: `sudo apt-get install cups-ipp-utils`) and
the brain venv (OpenCV). The printer's address is never in the repo: pass
--printer or set MARKER_PRINTER (host or host:port).

    scripts/print_marker.py hardware/markers/aruco_4x4_50_id2_60mm.png --printer <host>
"""
import argparse
import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2

DPI = 300

TEST = """{
  NAME "Print-Job marker page"
  OPERATION Print-Job
  GROUP operation-attributes-tag
  ATTR charset attributes-charset utf-8
  ATTR naturalLanguage attributes-natural-language en
  ATTR uri printer-uri $uri
  ATTR name requesting-user-name grover
  ATTR name job-name "$jobname"
  ATTR mimeMediaType document-format image/jpeg
  GROUP job-attributes-tag
  ATTR keyword media na_letter_8.5x11in
  ATTR keyword print-scaling none
  ATTR keyword print-color-mode monochrome
  ATTR enum print-quality 5
  ATTR integer copies $copies
  FILE $filename
  STATUS successful-ok
  STATUS successful-ok-ignored-or-substituted-attributes
  EXPECT job-id OF-TYPE integer WITH-VALUE >0
  DISPLAY job-id
  DISPLAY job-state
}
"""


def png_to_jpeg_300dpi(png: Path, jpg: Path) -> None:
    img = cv2.imread(str(png), cv2.IMREAD_GRAYSCALE)
    if img is None:
        sys.exit(f"cannot read {png}")
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    if not ok:
        sys.exit("jpeg encode failed")
    data = bytearray(buf.tobytes())
    # JFIF APP0 right after SOI: FF E0 len 'JFIF\0' ver(2) units(1) xd(2) yd(2)
    assert data[2:4] == b"\xff\xe0" and data[6:11] == b"JFIF\x00", "no JFIF APP0 to patch"
    data[13:18] = struct.pack(">BHH", 1, DPI, DPI)   # units=1 -> dots per inch
    jpg.write_bytes(data)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("png", type=Path)
    ap.add_argument("--printer", default=os.environ.get("MARKER_PRINTER"), help="host[:port] (or $MARKER_PRINTER)")
    ap.add_argument("--copies", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true", help="write the JPEG and test file, don't print")
    a = ap.parse_args()
    if not a.printer:
        sys.exit("printer address: --printer or MARKER_PRINTER")
    with tempfile.TemporaryDirectory() as td:
        jpg = Path(td) / (a.png.stem + ".jpg")
        png_to_jpeg_300dpi(a.png, jpg)
        test = Path(td) / "print-marker.test"
        test.write_text(TEST)
        cmd = ["ipptool", "-tv", "-f", str(jpg), "-d", f"jobname={a.png.stem}", "-d", f"copies={a.copies}",
               f"ipp://{a.printer}/ipp/print", str(test)]
        print(" ".join(cmd))
        if a.dry_run:
            print(f"dry run: {jpg} ({jpg.stat().st_size} bytes)")
            return
        sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
