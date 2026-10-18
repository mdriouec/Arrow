"""
Configuration and settings management for Arrow.
Handles persistent user preferences and download history.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List


class ConfigManager:
    """Manages application settings and download history stored in ~/.config/arrow/"""

    CONFIG_DIR = Path.home() / ".config" / "arrow"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    LEGACY_DIR = Path.home() / ".config" / "yt_downloader"
    LEGACY_FILE = LEGACY_DIR / "config.json"

    DEFAULT_SETTINGS: Dict[str, Any] = {
        "download_dir": "",
        "media_mode": "video",  # "video" or "audio"
        "video_quality": "best",  # "best", "2160", "1440", "1080", "720"
        "video_format": "mp4",  # "mp4", "mkv", "webm"
        "audio_format": "mp3",  # "mp3", "flac", "m4a", "opus", "best"
        "audio_quality": "320",  # "320", "256", "192"
        "embed_thumbnail": True,
        "embed_metadata": True,
        "concurrent_fragments": 8,  # Multi-threaded turbo chunk downloading
        "history": [],
    }

    def __init__(self) -> None:
        self.settings: Dict[str, Any] = dict(self.DEFAULT_SETTINGS)
        self._ensure_config_dir()
        self.load()

        # Set default download directory if not specified or doesn't exist
        if not self.settings.get("download_dir") or not os.path.exists(self.settings["download_dir"]):
            self.settings["download_dir"] = self.get_default_download_dir()
            self.save()

    def _ensure_config_dir(self) -> None:
        """Create configuration directory if it doesn't exist."""
        try:
            self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"Warning: Could not create config dir {self.CONFIG_DIR}: {e}")

    @staticmethod
    def get_default_download_dir() -> str:
        """Determine the default download directory (XDG Downloads or ~/Downloads)."""
        xdg_download = os.environ.get("XDG_DOWNLOAD_DIR")
        if xdg_download and os.path.isdir(xdg_download):
            return xdg_download

        downloads_path = Path.home() / "Downloads"
        if not downloads_path.exists():
            try:
                downloads_path.mkdir(parents=True, exist_ok=True)
            except OSError:
                return str(Path.home())
        return str(downloads_path)

    def load(self) -> None:
        """Load settings from JSON file with backward-compatibility migration."""
        file_to_load = self.CONFIG_FILE
        if not file_to_load.exists() and self.LEGACY_FILE.exists():
            file_to_load = self.LEGACY_FILE

        if not file_to_load.exists():
            return

        try:
            with open(file_to_load, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self.settings.update(data)
        except Exception as e:
            print(f"Error loading config file: {e}")

    def save(self) -> None:
        """Save current settings to JSON file."""
        try:
            self._ensure_config_dir()
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve setting value."""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any, auto_save: bool = True) -> None:
        """Set a setting value and optionally save."""
        self.settings[key] = value
        if auto_save:
            self.save()

    def add_history(self, item: Dict[str, Any], max_items: int = 30) -> None:
        """Add a downloaded item to recent history."""
        history: List[Dict[str, Any]] = self.settings.get("history", [])
        history = [h for h in history if h.get("file_path") != item.get("file_path")]
        history.insert(0, item)
        self.settings["history"] = history[:max_items]
        self.save()

    def remove_history_item(self, file_path: str) -> None:
        """Remove a specific item from history by file_path."""
        history: List[Dict[str, Any]] = self.settings.get("history", [])
        self.settings["history"] = [h for h in history if h.get("file_path") != file_path]
        self.save()

    def clear_history(self) -> None:
        """Clear the download history."""
        self.settings["history"] = []
        self.save()
