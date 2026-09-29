"""
Thin client for the rover's ESPHome native API.

Wraps aioesphomeapi with the two things the brain needs: fire a drive
service, and read the latest state of the sensors the firmware exposes
(motion, battery voltage, cliff sensors). Connection details come from the
environment - never from files in this repo.

    ROVER_HOST      IP or mDNS name of the rover
    ROVER_PORT      native API port (default 6053)
    ROVER_API_KEY   base64 native-API encryption key
"""
import asyncio
import os
from dataclasses import dataclass, field
from typing import Optional

from aioesphomeapi import APIClient

DRIVE_SERVICES = ("forward", "backward", "left", "right")


@dataclass
class RoverState:
    motion: Optional[str] = None
    battery_voltage: Optional[float] = None
    front_left_cliff: Optional[bool] = None
    front_right_cliff: Optional[bool] = None
    uptime_s: Optional[float] = None
    wifi_dbm: Optional[float] = None
    brake_on_stop: Optional[bool] = None
    raw: dict = field(default_factory=dict)


class RoverClient:
    def __init__(self):
        self.host = os.environ.get("ROVER_HOST", "rover.local")
        self.port = int(os.environ.get("ROVER_PORT", "6053"))
        key = os.environ.get("ROVER_API_KEY")
        if not key:
            raise RuntimeError("ROVER_API_KEY is not set")
        self._key = key

    async def _connect(self) -> APIClient:
        client = APIClient(self.host, self.port, password=None, noise_psk=self._key)
        await client.connect(login=True)
        return client

    async def state(self, timeout: float = 5.0) -> RoverState:
        client = await self._connect()
        try:
            entities, _ = await client.list_entities_services()
            by_key = {e.key: e.object_id for e in entities}
            seen: dict = {}
            done = asyncio.Event()

            def on_state(st):
                seen[st.key] = st
                if len(seen) >= len(by_key):
                    done.set()

            client.subscribe_states(on_state)
            try:
                await asyncio.wait_for(done.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                pass
            out = RoverState()
            for key, oid in by_key.items():
                st = seen.get(key)
                if st is None:
                    continue
                val = getattr(st, "state", None)
                out.raw[oid] = val
                if oid == "motion":
                    out.motion = val
                elif oid == "battery_voltage":
                    out.battery_voltage = float(val)
                elif oid == "front_left_cliff":
                    out.front_left_cliff = bool(val)
                elif oid == "front_right_cliff":
                    out.front_right_cliff = bool(val)
                elif oid.endswith("uptime"):
                    out.uptime_s = float(val)
                elif oid.endswith("wifi_signal"):
                    out.wifi_dbm = float(val)
                elif oid == "brake_on_stop":
                    out.brake_on_stop = bool(val)
            return out
        finally:
            await client.disconnect()

    async def drive(self, direction: str, seconds: float) -> None:
        """Fire a drive service, hold for `seconds`, then stop. The firmware
        also stops on its own if this connection drops or 1.5s passes
        without a refresh, so a crash here cannot leave the motors running."""
        if direction not in DRIVE_SERVICES:
            raise ValueError(f"direction must be one of {DRIVE_SERVICES}")
        client = await self._connect()
        try:
            _, services = await client.list_entities_services()
            svc = {s.name: s for s in services}
            await client.execute_service(svc[direction], {})
            await asyncio.sleep(seconds)
            await client.execute_service(svc["stop"], {})
            await asyncio.sleep(0.2)
        finally:
            await client.disconnect()

    async def set_switch(self, object_id: str, on: bool) -> None:
        """Turn a firmware switch entity (e.g. brake_on_stop) on or off."""
        client = await self._connect()
        try:
            entities, _ = await client.list_entities_services()
            match = [e for e in entities if e.object_id == object_id]
            if not match:
                raise ValueError(f"no entity {object_id!r} on the rover")
            client.switch_command(match[0].key, on)
            await asyncio.sleep(0.3)
        finally:
            await client.disconnect()

    async def stop(self) -> None:
        client = await self._connect()
        try:
            _, services = await client.list_entities_services()
            svc = {s.name: s for s in services}
            await client.execute_service(svc["stop"], {})
            await asyncio.sleep(0.2)
        finally:
            await client.disconnect()
