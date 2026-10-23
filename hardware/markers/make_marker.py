#!/usr/bin/env python3
"""
Generate a printable ArUco marker page for visual homing.

Default: dictionary 4x4_50, id 0, 80 mm square, centred on a US Letter page
at 300 DPI with a thick white quiet zone (the detector needs it), a caption
and a 100 mm scale bar with 10 mm ticks. Print at 100% scale - no "fit to
page" - and check the scale bar with a ruler; the brain's distance estimate
assumes the printed size. `--front` adds a "FRONT" label on the marker's
top edge, which is the forward direction `brain/overhead.py` reads from it
(the rover's top marker goes on with that edge toward the nose).

    usage: make_marker.py [--id 0] [--size-mm 80] [--front] [--out aruco_4x4_50_id0_80mm.png]

Printing over the network from this repo: `scripts/print_marker.py`.
"""
import argparse
import cv2
import numpy as np

DPI = 300
PAGE_W_IN, PAGE_H_IN = 8.5, 11.0
MM = DPI / 25.4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", type=int, default=0)
    ap.add_argument("--size-mm", type=float, default=80.0)
    ap.add_argument("--front", action="store_true", help="label the top edge FRONT (rover top marker)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or f"aruco_4x4_50_id{a.id}_{int(a.size_mm)}mm.png"

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    px = int(round(a.size_mm * MM))
    marker = cv2.aruco.generateImageMarker(dictionary, a.id, px)

    page = np.full((int(PAGE_H_IN * DPI), int(PAGE_W_IN * DPI)), 255, np.uint8)
    y0 = (page.shape[0] - px) // 2 - int(0.5 * DPI)
    x0 = (page.shape[1] - px) // 2
    page[y0:y0 + px, x0:x0 + px] = marker

    if a.front:
        label = "FRONT  (this edge toward the nose)"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.6, 4)
        cv2.putText(page, label, (x0 + px // 2 - tw // 2, y0 - int(0.45 * DPI)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.6, 0, 4, cv2.LINE_AA)
        # arrow from the label down to the marker's top edge
        ax = x0 + px // 2
        cv2.arrowedLine(page, (ax, y0 - int(0.38 * DPI)), (ax, y0 - int(0.08 * DPI)), 0, 4, tipLength=0.4)

    caption = f"rover marker  |  ArUco 4x4_50 id {a.id}  |  {a.size_mm:g} mm square  |  print at 100%"
    cy = y0 + px + int(0.6 * DPI)
    cv2.putText(page, caption, (x0 - int(1.2 * DPI), cy),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, 0, 3, cv2.LINE_AA)

    # 100 mm scale bar, 10 mm ticks: the printed-size check is a ruler on this bar
    bx0 = page.shape[1] // 2 - int(50 * MM)
    by = cy + int(0.7 * DPI)
    cv2.line(page, (bx0, by), (bx0 + int(100 * MM), by), 0, 4)
    for i in range(11):
        x = bx0 + int(round(i * 10 * MM))
        h = int(4 * MM) if i % 5 == 0 else int(2 * MM)
        cv2.line(page, (x, by - h), (x, by + h), 0, 4)
    cv2.putText(page, "0", (bx0 - 12, by + int(7 * MM)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, 0, 2, cv2.LINE_AA)
    cv2.putText(page, "100 mm", (bx0 + int(100 * MM) - 60, by + int(7 * MM)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, 0, 2, cv2.LINE_AA)

    cv2.imwrite(out, page)
    print(f"wrote {out}: marker {px}px = {a.size_mm:g} mm at {DPI} DPI, page {page.shape[1]}x{page.shape[0]}")


if __name__ == "__main__":
    main()
