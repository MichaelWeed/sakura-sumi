#!/bin/bash
# Convenience script to compress a directory with default settings
# Used by macOS Automator workflows for right-click compression

set -e  # Exit on error

# Get the directory passed as argument (from Finder/right-click)
SOURCE_DIR="${1:-$(pwd)}"

# Handle placeholder paths or help requests
if [ "$SOURCE_DIR" = "/path/to/test" ] || [ "$SOURCE_DIR" = "--help" ] || [ "$SOURCE_DIR" = "-h" ]; then
    echo "Usage: $0 [directory_path]" >&2
    echo "" >&2
    echo "Compresses a directory to PDFs using default settings." >&2
    echo "" >&2
    echo "Examples:" >&2
    echo "  $0                          # Compress current directory" >&2
    echo "  $0 /path/to/your/codebase  # Compress specified directory" >&2
    echo "  $0 ~/Projects/my-project    # Compress using home directory shortcut" >&2
    echo "" >&2
    echo "If no directory is specified, the current directory is used." >&2
    exit 1
fi

# Resolve to absolute path
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Directory does not exist: $SOURCE_DIR" >&2
    echo "" >&2
    echo "💡 Tip: Make sure the path is correct. You can:" >&2
    echo "   - Use an absolute path: /Users/yourname/Projects/myproject" >&2
    echo "   - Use a relative path: ./myproject" >&2
    echo "   - Use home shortcut: ~/Projects/myproject" >&2
    echo "   - Omit the path to compress the current directory" >&2
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
    echo "" >&2
    if [ "$VENV_ACTIVATED" = true ]; then
        echo "Virtual environment is activated, but dependencies are missing." >&2
        echo "Please run:" >&2
        echo "  pip install -r requirements.txt" >&2
    else
        echo "No virtual environment found. Please:" >&2
        echo "  1. Create venv: python3 -m venv venv" >&2
        echo "  2. Activate it: source venv/bin/activate" >&2
        echo "  3. Install deps: pip install -r requirements.txt" >&2
    fi
    if [ "$VENV_ACTIVATED" = true ]; then
        deactivate
    fi
    exit 1
fi

# Run compression with default settings (smart concatenation enabled by default)
# Capture both stdout and stderr to ensure errors are visible in Automator
if ! python3 scripts/compress.py "$SOURCE_DIR" -v 2>&1; then
    EXIT_CODE=$?
    # Deactivate virtual environment if it was activated
    if [ "$VENV_ACTIVATED" = true ]; then
        deactivate
    fi
    exit $EXIT_CODE
fi
EXIT_CODE=$?

# Deactivate virtual environment if it was activated
if [ "$VENV_ACTIVATED" = true ]; then
    deactivate
fi

exit $EXIT_CODE
