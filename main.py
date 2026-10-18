#!/usr/bin/env python3
"""
Arrow - Modern High-Speed Linux Video & Music Downloader
Entry point for the application.
"""

import os
import sys

# Display and session robustness for Linux desktops (Wayland / X11 / Headless)
xdg_runtime = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
wayland_disp = os.environ.get("WAYLAND_DISPLAY")
wayland_sock = os.path.join(xdg_runtime, wayland_disp) if wayland_disp else None
has_wayland = bool(wayland_sock and os.path.exists(wayland_sock))
has_x11 = bool(os.environ.get("DISPLAY"))

if not has_wayland and not has_x11:
    if "QT_QPA_PLATFORM" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["QT_QPA_PLATFORMTHEME"] = ""
elif not has_wayland and wayland_disp:
    # Wayland variable is stale or socket inaccessible; unset to allow X11 / Xcb fallback
    del os.environ["WAYLAND_DISPLAY"]

if "DBUS_SESSION_BUS_ADDRESS" not in os.environ and "QT_QPA_PLATFORMTHEME" not in os.environ:
    os.environ["QT_QPA_PLATFORMTHEME"] = ""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from app.config import ConfigManager
from app.ui.icons import IconFactory
from app.ui.main_window import MainWindow
from app.ui.styles import MAIN_STYLESHEET


def main() -> int:
    """Initialize and run Arrow application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Arrow")
    app.setApplicationDisplayName("Arrow — High-Speed Video & Music Downloader")
    app.setOrganizationName("Arrow")
    app.setDesktopFileName("arrow.desktop")

    # Set application icon
    app_icon = IconFactory.get_icon("app_logo", size=64)
    app.setWindowIcon(app_icon)

    # Apply modern stylesheet
    app.setStyleSheet(MAIN_STYLESHEET)

    # Initialize configuration
    config = ConfigManager()

    # Create and display main window
    window = MainWindow(config)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
