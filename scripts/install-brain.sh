#!/usr/bin/env bash
# Installs the rover brain (MCP server) into a virtualenv at brain/.venv.
# Open-source deps only: the official MCP Python SDK, aioesphomeapi (the
# ESPHome native-API client), OpenCV (headless) + numpy for marker detection.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$ROOT/brain/.venv"
python3 -m venv "$VENV"
"$VENV/bin/pip" install -q --upgrade pip
# (was one line with a comment in the middle - only mcp got installed; 2026-10-05)
"$VENV/bin/pip" install -q -r "$ROOT/brain/requirements.txt"
echo "installed into $VENV"
"$VENV/bin/python" -c "import mcp, aioesphomeapi, cv2; print('mcp', mcp.__version__ if hasattr(mcp,'__version__') else 'ok', '| cv2', cv2.__version__)"
