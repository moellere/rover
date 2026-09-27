#!/usr/bin/env python3
"""
Minimal CLI for driving the rover directly over ESPHome's native API,
bypassing Home Assistant entirely. Useful for scripted/teleop control
and for testing the firmware's safety behaviors (command watchdog,
disconnect-triggered stop).

Usage:
    ROVER_HOST=<ip-or-hostname> ROVER_API_KEY=<base64-key> \\
        python3 rover_ctl.py <list|forward|backward|left|right|stop> [duration_seconds]

    - `list` prints the device's entities and available services.
    - Any other command fires that service; with a duration, it sleeps
      that long and then calls `stop` (a pulse rather than a hold).

Env vars:
    ROVER_HOST     IP or mDNS hostname of the rover's ESPHome device.
    ROVER_PORT     Native API port (default 6053).
    ROVER_API_KEY  Base64-encoded ESPHome native API encryption key
                   (from that device's `api.encryption.key` in its
                   ESPHome YAML / secrets file).

Requires: aioesphomeapi (pip install aioesphomeapi)
"""
import asyncio
import os
import sys

from aioesphomeapi import APIClient

HOST = os.environ.get("ROVER_HOST", "rover.local")
PORT = int(os.environ.get("ROVER_PORT", "6053"))


def get_api_key() -> str:
    key = os.environ.get("ROVER_API_KEY")
    if not key:
        raise SystemExit(
            "Set ROVER_API_KEY to the device's base64 native-API encryption key."
        )
    return key


async def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    duration = float(sys.argv[2]) if len(sys.argv) > 2 else None

    client = APIClient(HOST, PORT, password=None, noise_psk=get_api_key())
    await client.connect(login=True)

    entities, services = await client.list_entities_services()

    if cmd == "list":
        print("=== Entities ===")
        for e in entities:
            print(f"  {type(e).__name__}: {e.object_id}")
        print("=== Services ===")
        for s in services:
            print(f"  {s.name} args={[a.name for a in s.args]}")
        await client.disconnect()
        return

    svc = next((s for s in services if s.name == cmd), None)
    if not svc:
        print(f"No such service: {cmd}. Available: {[s.name for s in services]}")
        await client.disconnect()
        return

    print(f"Executing service: {cmd}")
    await client.execute_service(svc, {})

    if duration:
        await asyncio.sleep(duration)
        stop_svc = next(s for s in services if s.name == "stop")
        print("Executing service: stop")
        await client.execute_service(stop_svc, {})
        await asyncio.sleep(0.3)

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
