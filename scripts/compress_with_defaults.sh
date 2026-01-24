#!/bin/bash
# Convenience script to compress a directory with default settings
# Used by macOS Automator workflows for right-click compression

set -e  # Exit on error

# Create log directory and file for debugging
LOG_DIR="$HOME/Library/Logs"
LOG_FILE="$LOG_DIR/sakura-sumi-quick-action.log"
mkdir -p "$LOG_DIR"

# Log function that writes to both stderr and log file
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE" >&2
}

# Immediate output for Automator visibility
log "🌸 Sakura Sumi: Starting compression..."
log "Number of arguments: $#"
log "All arguments: $@"
log "Argument 1: '${1:-none}'"

# Get the directory passed as argument (from Finder/right-click)
# Automator may pass paths in different ways - handle multiple cases
if [ $# -eq 0 ]; then
    # No arguments - use current directory
    SOURCE_DIR="$(pwd)"
    log "No arguments provided, using current directory: $SOURCE_DIR"
elif [ $# -eq 1 ]; then
    # Single argument - use it directly
    SOURCE_DIR="$1"
    log "Using single argument: $SOURCE_DIR"
else
    # Multiple arguments - Automator might pass each file/folder separately
    # For Quick Actions on folders, take the first one
    SOURCE_DIR="$1"
    log "Multiple arguments provided, using first: $SOURCE_DIR"
    log "All provided paths: $@"
fi

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
log "Checking directory: '$SOURCE_DIR'"

# Handle special characters and spaces in path
# Remove any quotes that might have been added
SOURCE_DIR=$(echo "$SOURCE_DIR" | sed "s/^['\"]//; s/['\"]$//")

# Expand ~ if present
SOURCE_DIR="${SOURCE_DIR/#\~/$HOME}"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Directory does not exist: '$SOURCE_DIR'" >&2
    echo "Resolved path: $(cd "$SOURCE_DIR" 2>&1 && pwd || echo 'failed')" >&2
    echo "" >&2
    echo "💡 Tip: Make sure the path is correct. You can:" >&2
    echo "   - Use an absolute path: /Users/yourname/Projects/myproject" >&2
    echo "   - Use a relative path: ./myproject" >&2
    echo "   - Use home shortcut: ~/Projects/myproject" >&2
    echo "   - Omit the path to compress the current directory" >&2
    exit 1
fi

# Resolve to absolute path (handles symlinks and relative paths)
SOURCE_DIR=$(cd "$SOURCE_DIR" && pwd)
log "Resolved to absolute path: $SOURCE_DIR"

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"
echo "Project root: $PROJECT_ROOT" >&2

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
# Use unbuffered Python output (-u) to ensure immediate output in Automator
log "Starting Python compression script..."
EXIT_CODE=0
if ! python3 -u scripts/compress.py "$SOURCE_DIR" -v 2>&1 | tee -a "$LOG_FILE"; then
    EXIT_CODE=$?
    log "Compression failed with exit code: $EXIT_CODE"
    # Deactivate virtual environment if it was activated
    if [ "$VENV_ACTIVATED" = true ]; then
        deactivate
    fi
    exit $EXIT_CODE
fi

# Deactivate virtual environment if it was activated
if [ "$VENV_ACTIVATED" = true ]; then
    deactivate
fi

exit $EXIT_CODE
