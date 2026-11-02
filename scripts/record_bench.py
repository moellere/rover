"""Record the overhead benchcam to an MP4 timelapse (2026-11-02).

Grabs snapshots from the camera's HTTP endpoint (brain.cameras.snapshot, the
same path `locate` uses) as fast as it serves them, burns in the elapsed time
and, if the rover answers, its battery and dock state, and encodes the frames
with the ffmpeg binary that imageio-ffmpeg bundles (no system ffmpeg needed).

    uv run --with imageio-ffmpeg --with pillow --with aioesphomeapi \
        python scripts/record_bench.py OUT.mp4 --seconds 240 [--fps 6] [--label "..."]

Stops after --seconds or on Ctrl-C/SIGTERM, then encodes. Needs the brain's
env (~/.rover-brain.env: BENCH_CAM_*, ROVER_*). Run from the repo root.
"""
import argparse
import asyncio
import io
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from brain.cameras import snapshot  # noqa: E402

stop = threading.Event()
telemetry = {"text": ""}


def poll_rover():
    """Battery / dock state every ~3 s for the overlay; silent if unreachable."""
    try:
        from brain.rover_client import RoverClient
    except Exception:
        return
    c = RoverClient()
    while not stop.is_set():
        try:
            s = asyncio.run(c.state(timeout=2.0))
            dock = "ON DOCK" if s.on_dock else ""
            telemetry["text"] = f"{s.battery_voltage:.2f} V  {s.motion or ''}  {dock}".strip()
        except Exception:
            pass
        stop.wait(3.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--seconds", type=float, default=240)
    ap.add_argument("--fps", type=float, default=6, help="playback frame rate")
    ap.add_argument("--label", default="Grover - benchcam")
    ap.add_argument("--width", type=int, default=1280)
    a = ap.parse_args()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop.set())
    threading.Thread(target=poll_rover, daemon=True).start()

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
    except OSError:
        font = ImageFont.load_default()
    tmp = tempfile.mkdtemp(prefix="benchrec-")
    t0 = time.monotonic()
    n = 0
    while not stop.is_set() and time.monotonic() - t0 < a.seconds:
        try:
            img = Image.open(io.BytesIO(snapshot("bench", timeout=5.0))).convert("RGB")
        except Exception:
            time.sleep(0.5)
            continue
        el = time.monotonic() - t0
        if img.width > a.width:
            img = img.resize((a.width, round(img.height * a.width / img.width)))
        d = ImageDraw.Draw(img)
        txt = f"{a.label}   t+{int(el // 60)}:{el % 60:04.1f}   {telemetry['text']}"
        d.rectangle([0, img.height - 52, img.width, img.height], fill=(0, 0, 0))
        d.text((14, img.height - 46), txt, fill=(255, 255, 255), font=font)
        img.save(os.path.join(tmp, f"f{n:05d}.jpg"), quality=88)
        n += 1
    stop.set()
    real = time.monotonic() - t0
    print(f"{n} frames over {real:.0f} s ({n / max(real, 1):.1f} frames/s)")
    if not n:
        sys.exit("no frames captured")
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-loglevel", "error", "-y", "-framerate", str(a.fps), "-i", os.path.join(tmp, "f%05d.jpg"),
                    "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", a.out], check=True)
    print(f"wrote {a.out} ({os.path.getsize(a.out) // 1024} KB, {n / a.fps:.0f} s at {a.fps} fps)")


if __name__ == "__main__":
    main()
