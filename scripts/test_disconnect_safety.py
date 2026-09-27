#!/usr/bin/env python3
"""
Regression test for the firmware's disconnect-triggered safety stop.

Simulates a crashed/hung controller: fires a `forward` command and then
disconnects immediately WITHOUT sending `stop`. If the firmware's
`api.on_client_disconnected` handler is working, the motors should be
stopped by the time we reconnect a couple seconds later - the `motion`
text sensor should read "Stopped" even though we deliberately never
told it to stop.

Env vars: same as rover_ctl.py (ROVER_HOST, ROVER_PORT, ROVER_API_KEY).
"""
import asyncio
import os

from aioesphomeapi import APIClient

HOST = os.environ.get("ROVER_HOST", "rover.local")
PORT = int(os.environ.get("ROVER_PORT", "6053"))


def get_api_key() -> str:
    key = os.environ.get("ROVER_API_KEY")
    if not key:
        raise SystemExit("Set ROVER_API_KEY to the device's base64 API key.")
    return key


async def main():
    key = get_api_key()

    # Phase 1: connect, fire forward, disconnect WITHOUT stopping (simulated crash).
    client = APIClient(HOST, PORT, password=None, noise_psk=key)
    await client.connect(login=True)
    _, services = await client.list_entities_services()
    fwd = next(s for s in services if s.name == "forward")
    print("Firing forward, then disconnecting immediately without stop...")
    await client.execute_service(fwd, {})
    await client.disconnect()
    print("Disconnected (simulated crash).")

    # Phase 2: wait, then reconnect and check the motion state.
    await asyncio.sleep(2.0)
    client2 = APIClient(HOST, PORT, password=None, noise_psk=key)
    await client2.connect(login=True)

    state_result = {}
    done = asyncio.Event()

    def on_state(state):
        state_result[state.key] = state
        done.set()

    entities, _ = await client2.list_entities_services()
    motion_entity = next(e for e in entities if e.object_id == "motion")
    client2.subscribe_states(on_state)
    try:
        await asyncio.wait_for(done.wait(), timeout=5)
    except asyncio.TimeoutError:
        pass

    st = state_result.get(motion_entity.key)
    result = st.state if st else "unknown"
    print(f"Motion state 2s after disconnect: {result}")
    print("PASS" if result == "Stopped" else "FAIL - motors may still be running!")
    await client2.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
