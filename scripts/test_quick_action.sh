#!/bin/bash
# Test script to verify Quick Action is working
# Use this in Automator to test if paths are being passed correctly

LOG_FILE="$HOME/Library/Logs/sakura-sumi-quick-action-test.log"
echo "=== QUICK ACTION TEST $(date) ===" >> "$LOG_FILE"
echo "Number of arguments: $#" >> "$LOG_FILE"
echo "All arguments: $@" >> "$LOG_FILE"
echo "Argument 1: '${1:-none}'" >> "$LOG_FILE"
echo "PWD: $(pwd)" >> "$LOG_FILE"
echo "PATH: $PATH" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Also show in dialog
osascript -e "display dialog \"Quick Action Test\n\nArguments: $#\nFirst: ${1:-none}\n\nCheck log: $LOG_FILE\" buttons {\"OK\"} default button \"OK\""
