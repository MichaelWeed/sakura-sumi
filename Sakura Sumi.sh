#!/bin/bash
# Double-click or run from terminal to install (if needed) and launch the web portal.
# Linux: make executable (chmod +x) and run from file manager or: ./Launch\ Sakura\ Sumi.sh

set -e
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

if ! python3 -c "import flask" 2>/dev/null; then
    pip install -q -r requirements.txt
fi

# Open browser if we have one (optional, non-blocking)
(sleep 2; xdg-open "http://localhost:5001" 2>/dev/null || true) &

# Run web portal (output to log so terminal stays silent)
LOG_FILE="$PROJECT_ROOT/sakura-sumi-web.log"
echo "Sakura Sumi running at http://localhost:5001 — Ctrl+C to quit."
exec python3 scripts/run_web.py >> "$LOG_FILE" 2>&1
