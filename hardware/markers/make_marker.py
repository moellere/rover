#!/usr/bin/env python3
"""
Generate a printable ArUco marker page for visual homing.

Default: dictionary 4x4_50, id 0, 80 mm square, centred on a US Letter page
at 300 DPI with a thick white quiet zone (the detector needs it) and a
caption. Print at 100% scale - no "fit to page" - and check the square with
a ruler; the brain's distance estimate assumes the printed size.

    usage: make_marker.py [--id 0] [--size-mm 80] [--out aruco_4x4_50_id0_80mm.png]
"""
import argparse
import cv2
import numpy as np

DPI = 300
PAGE_W_IN, PAGE_H_IN = 8.5, 11.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", type=int, default=0)
    ap.add_argument("--size-mm", type=float, default=80.0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or f"aruco_4x4_50_id{a.id}_{int(a.size_mm)}mm.png"

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    px = int(round(a.size_mm / 25.4 * DPI))
    marker = cv2.aruco.generateImageMarker(dictionary, a.id, px)

    page = np.full((int(PAGE_H_IN * DPI), int(PAGE_W_IN * DPI)), 255, np.uint8)
    y0 = (page.shape[0] - px) // 2 - int(0.5 * DPI)
    x0 = (page.shape[1] - px) // 2
    page[y0:y0 + px, x0:x0 + px] = marker
    caption = f"rover homing marker  |  ArUco 4x4_50 id {a.id}  |  {a.size_mm:g} mm square  |  print at 100%"
    cv2.putText(page, caption, (x0 - int(1.2 * DPI), y0 + px + int(0.6 * DPI)),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, 0, 3, cv2.LINE_AA)
    cv2.imwrite(out, page)
    print(f"wrote {out}: marker {px}px = {a.size_mm:g} mm at {DPI} DPI, page {page.shape[1]}x{page.shape[0]}")


if __name__ == "__main__":
    main()
