#!/bin/bash
# Run once to add "Sakura Sumi" to your application menu (Linux).
# Creates ~/.local/share/applications/sakura-sumi.desktop pointing at this project.

set -e
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$PROJECT_ROOT/Launch Sakura Sumi.sh"
mkdir -p "$HOME/.local/share/applications"
DESKTOP="$HOME/.local/share/applications/sakura-sumi.desktop"

cat > "$DESKTOP" << EOF
[Desktop Entry]
Type=Application
Name=Sakura Sumi
Comment=OCR Compression System - launch web portal
Exec=$LAUNCHER
Path=$PROJECT_ROOT
Terminal=true
Categories=Development;Utility;
EOF

echo "Installed. You can now launch 'Sakura Sumi' from your application menu."
echo "Or double-click 'Launch Sakura Sumi.sh' in this folder."
