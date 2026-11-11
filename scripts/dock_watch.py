"""Unattended charge watch (2026-11-11, Enoch away): one check per run, for cron.

Grover sits in front of the dock with the contact arms UP (not charging). When the
battery reading drops to --low volts, press `Arms down` and confirm pad voltage; on
contact it stays down and charges, without contact the arms go back up. Either way
it acts once (a flag file stops later runs) and logs every run.

    */15 * * * * cd <repo> && set -a && . ~/.rover-brain.env && set +a && \
        brain/.venv/bin/python scripts/dock_watch.py --low 11.0

Log and flag: ~/.local/state/rover-dock-watch.{log,done}. Delete the flag to re-arm.
It never drives: arms only.
"""
import argparse
import asyncio
import datetime
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain.rover_client import RoverClient  # noqa: E402

STATE = Path.home() / ".local" / "state"
LOG = STATE / "rover-dock-watch.log"
FLAG = STATE / "rover-dock-watch.done"
CONTACT_V = 9.0


def log(msg: str) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as fh:
        fh.write(f"{datetime.datetime.now().isoformat(timespec='seconds')} {msg}\n")


async def contact(c: RoverClient) -> tuple[bool, float | None]:
    good, v = 0, None
    for _ in range(5):
        st = await c.state(timeout=4.0)
        v = st.dock_voltage
        good = good + 1 if (st.on_dock and (v or 0.0) >= CONTACT_V) else 0
        if good >= 2:
            return True, v
        await asyncio.sleep(1.5)
    return False, v


async def main(low: float) -> None:
    if FLAG.exists():
        return
    c = RoverClient()
    try:
        st = await c.state(timeout=4.0)
    except Exception as e:  # rover off / unreachable: note it, try again next run
        log(f"unreachable: {e!r}")
        return
    log(f"battery {st.battery_voltage} V, dock {st.dock_voltage} V, on_dock {st.on_dock}, "
        f"arms L {st.left_arm} R {st.right_arm}")
    if st.on_dock and (st.dock_voltage or 0.0) >= CONTACT_V:
        log("already on the dock - nothing to do")
        FLAG.write_text("already docked\n")
        return
    if st.battery_voltage is None or st.battery_voltage > low:
        return
    await c.press("arms_down")
    await asyncio.sleep(2.0)
    ok, v = await contact(c)
    if ok:
        log(f"ARMS DOWN at {st.battery_voltage:.2f} V: contact, charging (dock {v:.2f} V)")
        FLAG.write_text(f"charging since {datetime.datetime.now().isoformat(timespec='seconds')}\n")
    else:
        await c.press("arms_up")
        log(f"ARMS DOWN at {st.battery_voltage:.2f} V: NO contact (dock {v} V) - arms back up, giving up")
        FLAG.write_text("no contact\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--low", type=float, default=11.0)
    asyncio.run(main(ap.parse_args().low))
