#!/usr/bin/env bash
# Starts the rover-brain MCP server over stdio. Reads connection details from
# ~/.rover-brain.env (hosts, ESPHome API key) - never from this repo.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$HOME/.env" ] && set -a && . "$HOME/.env" && set +a
[ -f "$HOME/.rover-brain.env" ] && set -a && . "$HOME/.rover-brain.env" && set +a
cd "$HERE" && exec "$HERE/brain/.venv/bin/python" -m brain.server
