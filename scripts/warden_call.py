#!/usr/bin/env python3
"""
Call one tool on the print-warden MCP server (Streamable HTTP) from a shell.

The warden owns slicing, staging and the start gate for the 3D printer; this
project submits prints through it rather than talking to Moonraker directly.
Useful when the MCP server isn't loaded into the current Claude session.

    export PRINT_WARDEN_URL=http://<warden-host>:8710   # no secrets, LAN only
    curl -F file=@part.stl "$PRINT_WARDEN_URL/upload"
    scripts/warden_call.py submit_job '{"printer":"covington","model":"part.stl","material":"PETG","quality":"standard","name":"part"}'
    scripts/warden_call.py job_status '{"job_id":"..."}'
    scripts/warden_call.py start_print '{"job_id":"...","authorized_by":"<quote the human's permission>"}'
    scripts/warden_call.py print_status '{"printer":"garagex4"}'

Runs with the brain's venv (scripts/install-brain.sh installs the `mcp` SDK).
"""
import asyncio
import json
import os
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

BASE = os.environ.get("PRINT_WARDEN_URL")
if not BASE:
    sys.exit("set PRINT_WARDEN_URL (e.g. http://host:8710)")


async def main(tool: str, args: dict) -> None:
    async with streamablehttp_client(BASE.rstrip("/") + "/mcp") as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.call_tool(tool, args)
            for c in res.content:
                print(getattr(c, "text", c))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    asyncio.run(main(sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}))
