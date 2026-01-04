#!/bin/bash
# LabControl Uninstaller
# Removes desktop entries, symlinks, and optionally the entire installation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_DIR="$HOME/.local/share/applications"
BIN_DIR="$HOME/.local/bin"

echo "Uninstalling LabControl..."

# Remove desktop entries
rm -f "$DESKTOP_DIR/labcontrol-gui.desktop"
rm -f "$DESKTOP_DIR/labcontrol-tui.desktop"

# Remove symlinks
rm -f "$BIN_DIR/labcontrol-gui"
rm -f "$BIN_DIR/labcontrol-tui"
rm -f "$BIN_DIR/labcontrol"

# Update desktop database
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

echo "Removed desktop entries and symlinks."
echo ""

read -p "Also remove the entire LabControl directory ($SCRIPT_DIR)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing $SCRIPT_DIR..."
    rm -rf "$SCRIPT_DIR"
    echo "LabControl completely removed."
else
    echo "Kept $SCRIPT_DIR - you can remove it manually if needed."
fi
