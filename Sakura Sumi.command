#!/bin/bash
# Double-click to install (if needed) and launch the Sakura Sumi web portal.
# macOS: place this file in the project root and double-click.

set -e
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# Create venv if missing
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install deps quietly if missing
if ! python3 -c "import flask" 2>/dev/null; then
    pip install -q -r requirements.txt
fi

# Open browser after a short delay (non-blocking)
(sleep 2; open "http://localhost:5001" 2>/dev/null) &

# Run web portal (output to log so terminal stays silent)
LOG_FILE="$PROJECT_ROOT/sakura-sumi-web.log"
echo "Sakura Sumi running at http://localhost:5001 — Ctrl+C to quit."
exec python3 scripts/run_web.py >> "$LOG_FILE" 2>&1
