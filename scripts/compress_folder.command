#!/bin/bash
# Double-clickable script to compress a folder
# Usage: Drag a folder onto this file, or double-click and enter path when prompted

# Get the folder path
if [ $# -eq 0 ]; then
    # No argument provided, prompt user
    FOLDER_PATH=$(osascript -e 'tell application "System Events" to set folderPath to choose folder with prompt "Select folder to compress:"' -e 'return POSIX path of folderPath' 2>/dev/null)
    
    if [ -z "$FOLDER_PATH" ]; then
        osascript -e 'display dialog "No folder selected. Exiting." buttons {"OK"} default button "OK"' 2>/dev/null
        exit 1
    fi
else
    FOLDER_PATH="$1"
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Run compression
cd "$PROJECT_ROOT"
bash scripts/compress_quick_action.sh "$FOLDER_PATH"

# Keep terminal open to see results
echo ""
echo "Press any key to close..."
read -n 1
