#!/bin/bash
# Convenience script to compress a directory with default settings
# Used by macOS Automator workflows for right-click compression

set -e  # Exit on error

# Get the directory passed as argument (from Finder/right-click)
SOURCE_DIR="${1:-$(pwd)}"

# Resolve to absolute path
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Directory does not exist: $SOURCE_DIR" >&2
    exit 1
fi
SOURCE_DIR=$(cd "$SOURCE_DIR" && pwd)

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
VENV_ACTIVATED=false
if [ -d "venv" ]; then
    source venv/bin/activate
    VENV_ACTIVATED=true
elif [ -d ".venv" ]; then
    source .venv/bin/activate
    VENV_ACTIVATED=true
fi

# Check if required Python packages are installed
if ! python3 -c "import reportlab" 2>/dev/null; then
    echo "Error: Required dependencies not installed." >&2
    echo "Please run: pip install -r requirements.txt" >&2
    if [ "$VENV_ACTIVATED" = true ]; then
        deactivate
    fi
    exit 1
fi

# Run compression with default settings (smart concatenation enabled by default)
python3 scripts/compress.py "$SOURCE_DIR" -v
EXIT_CODE=$?

# Deactivate virtual environment if it was activated
if [ "$VENV_ACTIVATED" = true ]; then
    deactivate
fi

exit $EXIT_CODE
