"""Docking repeatability trials (2026-11-07).

Each cycle, starting with Grover on the dock: back straight off, drive to a
random start spot in a safe box mid-bench, turn to a random heading, then
`dock()` - and record whether it made contact, how far from the taught pose it
ended, how long it took and every step. Stops at the first failure unless
--keep-going, so a person can look before the next run.

ATTENDED ONLY: someone at the bench, lane clear, hands off.

    cd <repo> && set -a && . ~/.rover-brain.env && set +a
    brain/.venv/bin/python scripts/dock_trials.py --cycles 10 [--seed N] [--keep-going]

Writes brain/runs/<date>-dock-trials.json (appended per cycle, so a crash
keeps what ran). The start box is in benchcam pixels: mid-bench, clear of the
open edge (brain/keepout.py), the hatch and the far-right clutter; re-check it
if the camera or the dock moves.
"""
import argparse
import asyncio
import datetime
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain import keepout  # noqa: E402
from brain.steer import _rover, dock, face, go_to, undock  # noqa: E402

START_BOX = {"x": (1320, 1500), "y": (460, 500)}   # benchcam px: right of the hatch (x 975-1195) so the
                                                   # body clears it, and >= 200 mm from the open edge so the
                                                   # random-heading turn there passes keepout.check_turn (11-07)
HEADINGS = (120.0, 240.0)                          # image-frame deg: roughly toward the dock end, +/- 60


def pose_now():
    rover, _ = _rover("bench")
    return None if rover is None else {"x_px": round(rover.x_px, 1), "y_px": round(rover.y_px, 1),
                                       "heading_deg": rover.heading_deg, "mm_per_px": rover.mm_per_px}


async def cycle(n: int, rng: random.Random) -> dict:
    t0 = time.monotonic()
    rec = {"cycle": n, "started": datetime.datetime.now().isoformat(timespec="seconds"), "start_pose": pose_now()}
    u = await undock()
    rec["undock"] = {"ok": u.get("ok"), "reason": u.get("reason"), "log": u.get("log")}
    if not u.get("ok"):
        return {**rec, "ok": False, "stage": "undock"}
    tx, ty = rng.uniform(*START_BOX["x"]), rng.uniform(*START_BOX["y"])
    th = rng.uniform(*HEADINGS)
    rec["target"] = {"x_px": round(tx), "y_px": round(ty), "heading_deg": round(th, 1)}
    g = await go_to(x_px=tx, y_px=ty, stop_mm=60.0)
    rec["go_to"] = {"ok": g.ok, "reason": g.reason, "steps": g.steps, "log": g.log}
    if not g.ok:
        return {**rec, "ok": False, "stage": "go_to"}
    f = await face(th, tol=5.0)
    rec["face"] = {"ok": f.ok, "reason": f.reason, "log": f.log}
    if not f.ok:
        return {**rec, "ok": False, "stage": "face"}
    rec["dock_start_pose"] = pose_now()
    d = await dock()
    rec["dock"] = {k: d.get(k) for k in ("ok", "reason", "charging", "volts", "pose")}
    rec["dock_log"] = d.get("log")
    rec["seconds"] = round(time.monotonic() - t0)
    return {**rec, "ok": bool(d.get("charging")), "stage": "dock"}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=10)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--keep-going", action="store_true")
    a = ap.parse_args()
    seed = a.seed if a.seed is not None else int(time.time())
    rng = random.Random(seed)
    for x in START_BOX["x"]:          # the box must sit inside the keep-out margin with room to spare
        for y in START_BOX["y"]:
            d = keepout.edge_mm(x, y, 1.0)
            assert d > keepout.TURN_MIN_MM + 5, f"start box corner ({x},{y}) only {d:.0f} mm from the edge"
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "brain", "runs",
                       f"{datetime.date.today().isoformat()}-dock-trials.json")
    results = []
    print(f"seed {seed}, {a.cycles} cycles, log {out}")
    for n in range(1, a.cycles + 1):
        r = await cycle(n, rng)
        results.append(r)
        with open(out, "w") as fh:
            json.dump({"seed": seed, "cycles": results}, fh, indent=1, default=str)
        print(f"cycle {n}: {'OK ' if r['ok'] else 'FAIL'} stage={r['stage']} "
              f"{(r.get('dock') or {}).get('reason') or r.get(r['stage'], {}).get('reason')} "
              f"({r.get('seconds', '?')} s)")
        if not r["ok"] and not a.keep_going:
            print("stopping at the first failure - look before the next run")
            break
    ok = sum(1 for r in results if r["ok"])
    print(f"\n{ok}/{len(results)} docked and charging")


if __name__ == "__main__":
    asyncio.run(main())
