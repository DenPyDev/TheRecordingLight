#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

if [[ ! -d "$VENV" ]]; then
    python3 -m venv "$VENV"
fi

"$VENV/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt"
exec "$VENV/bin/python" "$SCRIPT_DIR/mic_monitor.py"
