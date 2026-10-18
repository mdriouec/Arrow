#!/usr/bin/env bash
#
# Install Arrow desktop shortcut for the current user
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$HOME/.local/share/applications"
TARGET_FILE="$TARGET_DIR/arrow.desktop"

mkdir -p "$TARGET_DIR"

# Generate desktop file with absolute paths
cat > "$TARGET_FILE" << EOF
[Desktop Entry]
Name=Arrow
GenericName=Video & Music Downloader
Comment=High-Speed Video & Music Downloader for Linux
Exec=$SCRIPT_DIR/run.sh
Icon=$SCRIPT_DIR/assets/icon.png
Terminal=false
Type=Application
Categories=AudioVideo;Network;
StartupNotify=true
StartupWMClass=arrow
Keywords=YouTube;Music;Video;Download;Audio;MP3;MP4;
EOF

chmod +x "$TARGET_FILE"

# Clean up legacy desktop shortcut if present
rm -f "$TARGET_DIR/pulsedl.desktop"

# Update desktop database if available
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$TARGET_DIR" 2>/dev/null
fi

echo "✓ Arrow desktop shortcut successfully installed to $TARGET_FILE"
echo "You can now launch Arrow directly from your Linux application menu!"
