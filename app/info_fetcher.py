"""
Worker thread for fetching media metadata and thumbnail previews.
Runs asynchronously with speed optimizations to ensure instantaneous preview.
"""

import urllib.request
from typing import Any, Dict, Optional
from PyQt6.QtCore import QThread, pyqtSignal
import yt_dlp

# Global in-memory cache for thumbnails to avoid duplicate network fetches
_THUMBNAIL_CACHE: Dict[str, bytes] = {}


def format_duration(seconds: Optional[int]) -> str:
    """Format seconds into HH:MM:SS or MM:SS."""
    if seconds is None or seconds < 0:
        return "Unknown"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def format_view_count(views: Optional[int]) -> str:
    """Format view count into human-readable compact notation."""
    if not views:
        return ""
    if views >= 1_000_000_000:
        return f"{views / 1_000_000_000:.1f}B views"
    if views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M views"
    if views >= 1_000:
        return f"{views / 1_000:.1f}K views"
    return f"{views:,} views"


class InfoFetchWorker(QThread):
    """Background worker that rapidly queries yt-dlp for media details without downloading."""

    started_fetching = pyqtSignal()
    info_loaded = pyqtSignal(dict)
    thumbnail_loaded = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)

    def __init__(self, url: str) -> None:
        super().__init__()
        self.url = url.strip()
        self._is_cancelled = False

    def cancel(self) -> None:
        """Flag the worker as cancelled."""
        self._is_cancelled = True

    def run(self) -> None:
        if not self.url:
            self.error_occurred.emit("Please enter a valid URL.")
            return

        self.started_fetching.emit()

        # Turbo info options: skip comments, skip manifests, skip playlists
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": "in_playlist",
            "noplaylist": True,
            "lazy_playlist": True,
            "socket_timeout": 8,
            "youtube_include_dash_manifest": False,
            "youtube_include_hls_manifest": False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)

            if self._is_cancelled:
                return

            if not info:
                self.error_occurred.emit("Could not retrieve media information.")
                return

            # If it's a playlist or multiple entries, pick the main video
            if "entries" in info and info["entries"]:
                entry = next((e for e in info["entries"] if e), None)
                if entry:
                    info = entry

            title = info.get("title", "Unknown Title")
            uploader = info.get("uploader") or info.get("channel") or info.get("artist") or "Unknown Creator"
            duration = info.get("duration")
            duration_str = format_duration(duration)
            views_str = format_view_count(info.get("view_count"))

            # Pick the best thumbnail
            thumbnail_url = info.get("thumbnail")
            thumbnails = info.get("thumbnails", [])
            if thumbnails and isinstance(thumbnails, list):
                valid_thumbs = [
                    t for t in thumbnails
                    if isinstance(t, dict) and t.get("url") and not t.get("url", "").endswith(".webp")
                ] or thumbnails
                best_thumb = max(valid_thumbs, key=lambda t: (t.get("preference", 0), t.get("width", 0) or 0), default=None)
                if best_thumb and best_thumb.get("url"):
                    thumbnail_url = best_thumb["url"]

            # Summarize available video heights/qualities
            formats = info.get("formats", [])
            available_resolutions = set()
            for f in formats:
                if isinstance(f, dict) and f.get("vcodec") != "none" and f.get("height"):
                    available_resolutions.add(f.get("height"))

            parsed_data = {
                "title": title,
                "uploader": uploader,
                "duration": duration,
                "duration_str": duration_str,
                "views_str": views_str,
                "thumbnail_url": thumbnail_url,
                "available_resolutions": sorted(list(available_resolutions), reverse=True),
                "webpage_url": info.get("webpage_url", self.url),
                "extractor_key": info.get("extractor_key", "Generic"),
            }

            self.info_loaded.emit(parsed_data)

            # Check thumbnail cache first
            if thumbnail_url and not self._is_cancelled:
                if thumbnail_url in _THUMBNAIL_CACHE:
                    self.thumbnail_loaded.emit(_THUMBNAIL_CACHE[thumbnail_url])
                else:
                    try:
                        req = urllib.request.Request(
                            thumbnail_url,
                            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
                        )
                        with urllib.request.urlopen(req, timeout=6) as response:
                            img_bytes = response.read()
                            if not self._is_cancelled and img_bytes:
                                _THUMBNAIL_CACHE[thumbnail_url] = img_bytes
                                self.thumbnail_loaded.emit(img_bytes)
                    except Exception as thumb_err:
                        print(f"Thumbnail download failed: {thumb_err}")

        except Exception as e:
            if not self._is_cancelled:
                err_msg = str(e)
                if "ERROR:" in err_msg:
                    err_msg = err_msg.split("ERROR:", 1)[1].strip()
                self.error_occurred.emit(err_msg)
