#!/usr/bin/env python3
"""
Print a marker page from hardware/markers/ on a network inkjet over IPP,
at exactly 100 % (no fit-to-page), so the ArUco square comes out the size
the brain assumes.

The page PNGs are 2550x3300 (US Letter at 300 DPI). The printer here is an
AirPrint-class inkjet that takes JPEG and PWG raster but not PDF. Default
is PWG raster (sgray_8 at the printer's 600 dpi, the page pixel-doubled so
the marker stays exact; run-length encoded per PWG 5102.4); `--format jpeg`
sends a 300 dpi JFIF JPEG with print-scaling=none instead. The media goes
as a full media-col (Letter, stationery, tray-1) matching the cassette
registration: with a bare `media` keyword this Canon accepted every job
and then stopped with support code 2110 ("size or type of the loaded
paper is different from the print settings"), which IPP only reports as
"other-error". Check the 100 mm scale bar with a ruler on the first print.

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
  ATTR mimeMediaType document-format $format
  GROUP job-attributes-tag
  ATTR collection media-col {
    MEMBER collection media-size {
      MEMBER integer x-dimension 21590
      MEMBER integer y-dimension 27940
    }
    MEMBER keyword media-type stationery
    MEMBER keyword media-source tray-1
  }
  ATTR keyword print-scaling none
  ATTR keyword print-color-mode monochrome
  ATTR enum print-quality 4
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
    # 3-channel on purpose: a 1-channel greyscale JPEG stalled the Canon twice
    # (job accepted, "processing" for ~2 min, then stopped and the printer hung)
    img = cv2.imread(str(png), cv2.IMREAD_COLOR)
    if img is None:
        sys.exit(f"cannot read {png}")
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90, cv2.IMWRITE_JPEG_PROGRESSIVE, 0])
    if not ok:
        sys.exit("jpeg encode failed")
    data = bytearray(buf.tobytes())
    # JFIF APP0 right after SOI: FF E0 len 'JFIF\0' ver(2) units(1) xd(2) yd(2)
    assert data[2:4] == b"\xff\xe0" and data[6:11] == b"JFIF\x00", "no JFIF APP0 to patch"
    data[13:18] = struct.pack(">BHH", 1, DPI, DPI)   # units=1 -> dots per inch
    jpg.write_bytes(data)


def page_to_pwg(png: Path, out: Path, dpi: int = 600) -> None:
    """Single-page PWG raster (sgray_8): 'RaS2' sync word, 1796-byte header
    (CUPS raster v2 layout with PWG's field meanings), RLE lines."""
    import numpy as np
    img = cv2.imread(str(png), cv2.IMREAD_GRAYSCALE)
    if img is None:
        sys.exit(f"cannot read {png}")
    f = dpi // DPI
    if f > 1:
        img = cv2.resize(img, None, fx=f, fy=f, interpolation=cv2.INTER_NEAREST)
    h, w = img.shape
    hdr = bytearray(1796)
    hdr[0:9] = b"PwgRaster"
    hdr[128:138] = b"stationery"
    struct.pack_into(">II", hdr, 276, dpi, dpi)            # HWResolution
    struct.pack_into(">I", hdr, 340, 1)                     # NumCopies
    struct.pack_into(">II", hdr, 352, 612, 792)             # PageSize (points)
    struct.pack_into(">II", hdr, 372, w, h)                 # Width, Height
    struct.pack_into(">IIII", hdr, 384, 8, 8, w, 0)         # BitsPerColor, BitsPerPixel, BytesPerLine, ColorOrder
    struct.pack_into(">I", hdr, 400, 18)                    # ColorSpace sGray
    struct.pack_into(">I", hdr, 420, 1)                     # NumColors
    struct.pack_into(">I", hdr, 452, 1)                     # TotalPageCount
    struct.pack_into(">ii", hdr, 456, 1, 1)                 # CrossFeed/FeedTransform
    struct.pack_into(">IIII", hdr, 464, 0, 0, w, h)         # ImageBox
    struct.pack_into(">I", hdr, 480, 0xFFFFFF)              # AlternatePrimary (white)
    struct.pack_into(">I", hdr, 484, 4)                     # PrintQuality normal
    name = b"na_letter_8.5x11in"
    hdr[1732:1732 + len(name)] = name

    def encode_line(row) -> bytes:
        out_ = bytearray()
        change = np.flatnonzero(np.diff(row.astype(np.int16))) + 1
        starts = np.concatenate(([0], change))
        ends = np.concatenate((change, [len(row)]))
        lits: list[int] = []
        def flush():
            i = 0
            while i < len(lits):
                chunk = lits[i:i + 128]
                out_.append(257 - len(chunk))
                out_.extend(chunk)
                i += 128
            lits.clear()
        for s0, e0 in zip(starts, ends):
            n = int(e0 - s0)
            v = int(row[s0])
            if n == 1:
                lits.append(v)
                continue
            flush()
            while n > 0:
                k = min(n, 128)
                out_.append(k - 1)
                out_.append(v)
                n -= k
        flush()
        return bytes(out_)

    body = bytearray()
    y = 0
    while y < h:
        n = 1
        while y + n < h and n < 256 and np.array_equal(img[y], img[y + n]):
            n += 1
        body.append(n - 1)
        body += encode_line(img[y])
        y += n
    out.write_bytes(b"RaS2" + bytes(hdr) + bytes(body))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("png", type=Path)
    ap.add_argument("--printer", default=os.environ.get("MARKER_PRINTER"), help="host[:port] (or $MARKER_PRINTER)")
    ap.add_argument("--copies", type=int, default=1)
    ap.add_argument("--format", choices=("pwg", "jpeg"), default="pwg")
    ap.add_argument("--dry-run", action="store_true", help="write the JPEG and test file, don't print")
    a = ap.parse_args()
    if not a.printer:
        sys.exit("printer address: --printer or MARKER_PRINTER")
    with tempfile.TemporaryDirectory() as td:
        if a.format == "pwg":
            jpg = Path(td) / (a.png.stem + ".pwg")
            page_to_pwg(a.png, jpg)
            fmt = "image/pwg-raster"
        else:
            jpg = Path(td) / (a.png.stem + ".jpg")
            png_to_jpeg_300dpi(a.png, jpg)
            fmt = "image/jpeg"
        test = Path(td) / "print-marker.test"
        test.write_text(TEST)
        cmd = ["ipptool", "-tv", "-f", str(jpg), "-d", f"jobname={a.png.stem}", "-d", f"copies={a.copies}", "-d", f"format={fmt}",
               f"ipp://{a.printer}/ipp/print", str(test)]
        print(" ".join(cmd))
        if a.dry_run:
            print(f"dry run: {jpg} ({jpg.stat().st_size} bytes)")
            return
        sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
