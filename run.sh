#!/usr/bin/env bash
#
# Arrow - High-Speed Video & Music Downloader for Linux
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install Python 3."
    exit 1
fi

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "Warning: ffmpeg is not installed or not in PATH. Audio/video stream merging may fail."
    echo "Install ffmpeg via your package manager: sudo apt install ffmpeg"
fi

# Run Arrow
exec python3 "$SCRIPT_DIR/main.py" "$@"
