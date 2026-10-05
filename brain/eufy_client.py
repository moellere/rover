"""
The Eufy RoboVac 12 over IR, through its lid board's ESPHome API.

The lid board (`blackcam` today, an ESP32-C3 later) exposes an
`eufy_command(command)` action that builds the remote's 6-byte frame
`68 CMD HH MM 5C SUM`, stamps the current time from SNTP (the vacuum
ignores stale frames) and sends it three times on a 38 kHz hardware
carrier. This client only names the commands.

    EUFY_HOST      lid board host
    EUFY_API_KEY   its native-API key (defaults to ROVER_API_KEY)

The Eufy has its own cliff, bumper and docking behaviour and runs on the
floor only (CLAUDE.md) - there is no courtesy layer here beyond that.
"""
import asyncio
import os

from aioesphomeapi import APIClient

COMMANDS = {"forward": 0x2C, "backward": 0x7C, "left": 0x3C, "right": 0x6C,
            "home": 0xEF, "start_stop": 0x4F}


class EufyClient:
    def __init__(self):
        self.host = os.environ.get("EUFY_HOST")
        self.key = os.environ.get("EUFY_API_KEY") or os.environ.get("ROVER_API_KEY")
        if not self.host or not self.key:
            raise RuntimeError("EUFY_HOST / EUFY_API_KEY not set")

    async def send(self, command: str) -> int:
        code = COMMANDS[command]
        c = APIClient(self.host, 6053, password=None, noise_psk=self.key)
        await c.connect(login=True)
        try:
            _, services = await c.list_entities_services()
            svc = {s.name: s for s in services}
            r = c.execute_service(svc["eufy_command"], {"command": code})
            if asyncio.iscoroutine(r):
                await r
            await asyncio.sleep(0.3)
        finally:
            await c.disconnect()
        return code
