#!/bin/bash
# LabControl Installer
# Installs desktop entries and creates symlinks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_DIR="$HOME/.local/share/applications"
BIN_DIR="$HOME/.local/bin"

echo "Installing LabControl..."

# Create directories
mkdir -p "$DESKTOP_DIR" "$BIN_DIR"

# Install desktop entries
cat > "$DESKTOP_DIR/labcontrol-gui.desktop" << EOF
[Desktop Entry]
Type=Application
Name=LabControl
Comment=Lab Equipment Control GUI
Exec=$SCRIPT_DIR/labcontrol-gui
Icon=utilities-system-monitor
Terminal=false
Categories=Science;Electronics;Development;
Keywords=oscilloscope;scope;lab;electronics;hantek;
StartupNotify=true
EOF

cat > "$DESKTOP_DIR/labcontrol-tui.desktop" << EOF
[Desktop Entry]
Type=Application
Name=LabControl TUI
Comment=Lab Equipment Control Terminal Interface
Exec=$SCRIPT_DIR/labcontrol-tui
Icon=utilities-terminal
Terminal=true
Categories=Science;Electronics;Development;ConsoleOnly;
Keywords=oscilloscope;scope;lab;electronics;hantek;terminal;
StartupNotify=true
EOF

# Create symlinks in ~/.local/bin (add to PATH if not already)
ln -sf "$SCRIPT_DIR/labcontrol-gui" "$BIN_DIR/labcontrol-gui"
ln -sf "$SCRIPT_DIR/labcontrol-tui" "$BIN_DIR/labcontrol-tui"
ln -sf "$SCRIPT_DIR/labcontrol-tui" "$BIN_DIR/labcontrol"  # Short alias

# Update desktop database
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

echo "Done!"
echo ""
echo "Installed:"
echo "  - Desktop entries (find LabControl in app menu)"
echo "  - Commands: labcontrol-gui, labcontrol-tui, labcontrol"
echo ""
echo "Make sure ~/.local/bin is in your PATH:"
echo "  fish:  set -U fish_user_paths ~/.local/bin \$fish_user_paths"
echo "  bash:  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
