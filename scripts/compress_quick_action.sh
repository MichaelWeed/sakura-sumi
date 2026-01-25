#!/bin/bash
# Enhanced Quick Action script with better error handling and notifications
# This version is designed specifically for Automator Quick Actions

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Create log directory and file
LOG_DIR="$HOME/Library/Logs"
LOG_FILE="$LOG_DIR/sakura-sumi-quick-action.log"
mkdir -p "$LOG_DIR"

# Log function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE" >&2
}

# Notification function (macOS)
notify() {
    local title="$1"
    local message="$2"
    osascript -e "display notification \"$message\" with title \"$title\"" 2>/dev/null || true
}

log "=== Quick Action Started ==="
log "Number of arguments: $#"
log "All arguments: $@"
log "PWD: $(pwd)"

# Get the directory passed as argument
if [ $# -eq 0 ]; then
    error_msg="No directory selected. Please right-click on a folder and select 'Compress with Sakura Sumi'."
    log "ERROR: $error_msg"
    notify "🌸 Sakura Sumi Error" "$error_msg"
    osascript -e "display dialog \"$error_msg\" buttons {\"OK\"} default button \"OK\" with icon stop" 2>/dev/null || true
    exit 1
fi

SOURCE_DIR="$1"
log "Processing directory: '$SOURCE_DIR'"

# Handle special characters and spaces in path
SOURCE_DIR=$(echo "$SOURCE_DIR" | sed "s/^['\"]//; s/['\"]$//")
SOURCE_DIR="${SOURCE_DIR/#\~/$HOME}"

# Validate directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    error_msg="Directory does not exist: $SOURCE_DIR"
    log "ERROR: $error_msg"
    notify "🌸 Sakura Sumi Error" "$error_msg"
    osascript -e "display dialog \"$error_msg\" buttons {\"OK\"} default button \"OK\" with icon stop" 2>/dev/null || true
    exit 1
fi

# Resolve to absolute path
SOURCE_DIR=$(cd "$SOURCE_DIR" && pwd)
log "Resolved path: $SOURCE_DIR"

# Get project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
log "Project root: $PROJECT_ROOT"

# Change to project root
cd "$PROJECT_ROOT"

# Activate virtual environment
VENV_ACTIVATED=false
if [ -d "venv" ]; then
    source venv/bin/activate
    VENV_ACTIVATED=true
    log "Virtual environment activated"
elif [ -d ".venv" ]; then
    source .venv/bin/activate
    VENV_ACTIVATED=true
    log "Virtual environment activated (.venv)"
fi

# Check dependencies
if ! python3 -c "import reportlab" 2>/dev/null; then
    error_msg="Required dependencies not installed. Please run: pip install -r requirements.txt"
    log "ERROR: $error_msg"
    notify "🌸 Sakura Sumi Error" "$error_msg"
    osascript -e "display dialog \"$error_msg\" buttons {\"OK\"} default button \"OK\" with icon stop" 2>/dev/null || true
    if [ "$VENV_ACTIVATED" = true ]; then
        deactivate
    fi
    exit 1
fi

# Show starting notification
notify "🌸 Sakura Sumi" "Starting compression of $(basename "$SOURCE_DIR")..."

# Run compression
log "Starting compression..."
OUTPUT_FILE=$(mktemp)
if python3 -u scripts/compress.py "$SOURCE_DIR" -v 2>&1 | tee -a "$LOG_FILE" "$OUTPUT_FILE"; then
    EXIT_CODE=0
    log "Compression completed successfully"
    
    # Get output directory
    OUTPUT_DIR="${SOURCE_DIR}_ocr_ready"
    
    # Show success notification
    notify "🌸 Sakura Sumi" "Compression complete! Output: $(basename "$OUTPUT_DIR")"
    
    # Optionally open the output directory
    # open "$OUTPUT_DIR"
else
    EXIT_CODE=$?
    error_msg="Compression failed with exit code: $EXIT_CODE. Check log: $LOG_FILE"
    log "ERROR: $error_msg"
    notify "🌸 Sakura Sumi Error" "Compression failed. Check log file."
    osascript -e "display dialog \"$error_msg\" buttons {\"OK\", \"View Log\"} default button \"OK\" with icon stop" 2>/dev/null || true
fi

# Cleanup
rm -f "$OUTPUT_FILE"
if [ "$VENV_ACTIVATED" = true ]; then
    deactivate
fi

log "=== Quick Action Finished (exit code: $EXIT_CODE) ==="
exit $EXIT_CODE
