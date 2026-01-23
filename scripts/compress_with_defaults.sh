#!/bin/bash
# Convenience script to compress a directory with default settings
# Used by macOS Automator workflows for right-click compression

# Get the directory passed as argument (from Finder/right-click)
SOURCE_DIR="${1:-$(pwd)}"

# Resolve to absolute path
SOURCE_DIR=$(cd "$SOURCE_DIR" && pwd)

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run compression with default settings (smart concatenation enabled by default)
python3 scripts/compress.py "$SOURCE_DIR" -v

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi
