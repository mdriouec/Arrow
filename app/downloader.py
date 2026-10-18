"""
High-Speed Download engine wrapping yt-dlp inside a PyQt6 QThread for Arrow.
Features multi-threaded concurrent fragment downloading (8x parallel connections),
10MB HTTP chunk pipeline, multi-core FFmpeg stream muxing, and granular live telemetry.
"""

import os
import re
import time
from typing import Any, Callable, Dict, Optional
from PyQt6.QtCore import QThread, pyqtSignal
import yt_dlp
from yt_dlp.utils import DownloadCancelled


def clean_ansi(text: str) -> str:
    """Remove ANSI escape sequences from strings."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def format_bytes(bytes_num: Optional[float]) -> str:
    """Convert bytes to human-readable size (KB, MB, GB)."""
    if not bytes_num or bytes_num < 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_num < 1024.0:
            return f"{bytes_num:.1f} {unit}" if unit != "B" else f"{int(bytes_num)} B"
        bytes_num /= 1024.0
    return f"{bytes_num:.1f} PB"


def format_speed(speed_bytes: Optional[float]) -> str:
    """Format download speed in human-readable notation."""
    if not speed_bytes or speed_bytes < 0:
        return "-- KB/s"
    return f"{format_bytes(speed_bytes)}/s"


def format_eta(eta_seconds: Optional[int]) -> str:
    """Format estimated time remaining."""
    if eta_seconds is None or eta_seconds < 0:
        return "--:--"
    m = eta_seconds // 60
    s = eta_seconds % 60
    if m >= 60:
        h = m // 60
        m = m % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


class DownloadWorker(QThread):
    """
    Executes media download via yt-dlp in a separate background thread with turbo acceleration.
    Emits granular progress, speed, ETA, status updates, completion and error signals.
    """

    progress_signal = pyqtSignal(dict)
    status_signal = pyqtSignal(str)
    completed_signal = pyqtSignal(dict)
    cancelled_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(
        self,
        url: str,
        download_dir: str,
        mode: str = "video",  # "video" or "audio"
        video_quality: str = "best",  # "best", "2160", "1440", "1080", "720"
        video_format: str = "mp4",  # "mp4", "mkv", "webm"
        audio_format: str = "mp3",  # "mp3", "flac", "m4a", "opus", "best"
        audio_quality: str = "320",  # "320", "256", "192"
        embed_thumbnail: bool = True,
        embed_metadata: bool = True,
        concurrent_fragments: int = 8,
    ) -> None:
        super().__init__()
        self.url = url.strip()
        self.download_dir = download_dir
        self.mode = mode
        self.video_quality = video_quality
        self.video_format = video_format
        self.audio_format = audio_format
        self.audio_quality = audio_quality
        self.embed_thumbnail = embed_thumbnail
        self.embed_metadata = embed_metadata
        self.concurrent_fragments = max(1, concurrent_fragments)

        self._is_cancelled = False
        self._final_filepath: Optional[str] = None
        self._last_progress_update = 0.0

    def cancel(self) -> None:
        """Request thread cancellation."""
        self._is_cancelled = True
        self.status_signal.emit("Cancelling download...")

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """Callback invoked by yt-dlp during download progress."""
        if self._is_cancelled:
            raise DownloadCancelled("Download cancelled by user.")

        status = d.get("status")
        now = time.time()

        if status == "downloading":
            # Throttle UI updates to ~25fps to prevent UI event loop congestion
            if now - self._last_progress_update < 0.04:
                return
            self._last_progress_update = now

            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            speed = d.get("speed")
            eta = d.get("eta")

            percent = 0.0
            if total > 0:
                percent = (downloaded / total) * 100.0
            else:
                pct_str = d.get("_percent_str")
                if pct_str:
                    try:
                        clean_pct = clean_ansi(pct_str).replace("%", "").strip()
                        percent = float(clean_pct)
                    except ValueError:
                        percent = 0.0

            filename = os.path.basename(d.get("filename", ""))
            status_text = "Downloading media stream..."
            if self.mode == "video":
                status_text = f"Turbo downloading best video & audio streams ({self.concurrent_fragments}x parallel)..."
            elif self.mode == "audio":
                status_text = f"Turbo downloading highest quality audio stream ({self.concurrent_fragments}x parallel)..."

            progress_data = {
                "percent": min(max(percent, 0.0), 100.0),
                "speed_str": format_speed(speed),
                "eta_str": format_eta(eta),
                "downloaded_bytes": downloaded,
                "total_bytes": total,
                "downloaded_str": format_bytes(downloaded),
                "total_str": format_bytes(total) if total > 0 else "Unknown",
                "status_text": status_text,
                "filename": filename,
            }
            self.progress_signal.emit(progress_data)

        elif status == "finished":
            filename = d.get("filename")
            if filename:
                self._final_filepath = filename
            self.status_signal.emit("Download finished. Processing media with multi-core FFmpeg...")

    def _postprocessor_hook(self, d: Dict[str, Any]) -> None:
        """Callback invoked by yt-dlp during FFmpeg postprocessing."""
        if self._is_cancelled:
            raise DownloadCancelled("Download cancelled by user.")

        status = d.get("status")
        pp_name = d.get("postprocessor", "")

        if status == "started":
            if pp_name == "Merger":
                self.status_signal.emit("Merging video & audio streams with multi-core FFmpeg...")
            elif pp_name == "ExtractAudio":
                self.status_signal.emit(f"Extracting high-fidelity {self.audio_format.upper()} audio...")
            elif pp_name == "FFmpegMetadata":
                self.status_signal.emit("Embedding media tags & chapter metadata...")
            elif pp_name == "EmbedThumbnail":
                self.status_signal.emit("Embedding high-resolution album cover art...")
            else:
                self.status_signal.emit(f"Applying FFmpeg processing ({pp_name})...")

        elif status == "finished":
            info_dict = d.get("info_dict", {})
            filepath = info_dict.get("filepath") or info_dict.get("_filename")
            if filepath:
                self._final_filepath = filepath

    def _build_yt_dlp_options(self) -> Dict[str, Any]:
        """Construct yt-dlp configuration options with turbo acceleration and highest quality."""
        os.makedirs(self.download_dir, exist_ok=True)

        out_template = os.path.join(self.download_dir, "%(title)s [%(id)s].%(ext)s")

        postprocessors = []

        if self.mode == "video":
            # Highest video + audio streams combined
            if self.video_quality == "2160":
                format_spec = "bestvideo[height<=2160]+bestaudio/best[height<=2160]/best"
            elif self.video_quality == "1440":
                format_spec = "bestvideo[height<=1440]+bestaudio/best[height<=1440]/best"
            elif self.video_quality == "1080":
                format_spec = "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"
            elif self.video_quality == "720":
                format_spec = "bestvideo[height<=720]+bestaudio/best[height<=720]/best"
            else:
                format_spec = "bestvideo+bestaudio/best"

            if self.embed_metadata:
                postprocessors.append({
                    "key": "FFmpegMetadata",
                    "add_chapters": True,
                    "add_metadata": True,
                })

            ydl_opts: Dict[str, Any] = {
                "format": format_spec,
                "outtmpl": out_template,
                "merge_output_format": self.video_format,
                "postprocessors": postprocessors,
            }

        else:
            # Music / Audio Mode - highest quality audio
            format_spec = "bestaudio/best"

            if self.audio_format != "best":
                extract_audio_pp = {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.audio_format,
                }
                if self.audio_format == "mp3":
                    extract_audio_pp["preferredquality"] = self.audio_quality or "320"
                elif self.audio_format in ("m4a", "opus"):
                    extract_audio_pp["preferredquality"] = "0"  # Best VBR

                postprocessors.append(extract_audio_pp)

            if self.embed_metadata:
                postprocessors.append({
                    "key": "FFmpegMetadata",
                    "add_metadata": True,
                })

            if self.embed_thumbnail:
                postprocessors.append({
                    "key": "EmbedThumbnail",
                    "already_have_thumbnail": False,
                })

            ydl_opts = {
                "format": format_spec,
                "outtmpl": out_template,
                "writethumbnail": self.embed_thumbnail,
                "postprocessors": postprocessors,
            }

        # Turbo Speed & Connection Performance Configuration
        ydl_opts.update({
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "concurrent_fragment_downloads": self.concurrent_fragments,
            "http_chunk_size": 10485760,  # 10 MB HTTP chunks to avoid throttle
            "buffersize": 1048576,        # 1 MB disk buffer
            "retries": 10,
            "fragment_retries": 10,
            "file_access_retries": 5,
            "postprocessor_args": {
                "ffmpeg": ["-threads", "0"],  # Multi-threaded FFmpeg acceleration
            },
            "progress_hooks": [self._progress_hook],
            "postprocessor_hooks": [self._postprocessor_hook],
        })

        return ydl_opts

    def run(self) -> None:
        if not self.url:
            self.error_signal.emit("Please enter a media URL.")
            return

        self.status_signal.emit("Connecting to media stream...")

        try:
            ydl_opts = self._build_yt_dlp_options()

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)

            if self._is_cancelled:
                self.cancelled_signal.emit()
                return

            if not info:
                self.error_signal.emit("Download failed: No media found at URL.")
                return

            title = info.get("title", "Media")
            duration = info.get("duration", 0)

            final_path = self._final_filepath
            if not final_path or not os.path.exists(final_path):
                req_downloads = info.get("requested_downloads", [])
                if req_downloads and isinstance(req_downloads, list):
                    for req in req_downloads:
                        p = req.get("filepath") or req.get("_filename")
                        if p and os.path.exists(p):
                            final_path = p
                            break

            if not final_path or not os.path.exists(final_path):
                expected_ext = self.video_format if self.mode == "video" else (
                    self.audio_format if self.audio_format != "best" else info.get("ext", "mp3")
                )
                safe_id = info.get("id", "")
                if safe_id:
                    for f in os.listdir(self.download_dir):
                        if safe_id in f and (f.endswith(f".{expected_ext}") or f.endswith(f".{self.video_format}")):
                            final_path = os.path.join(self.download_dir, f)
                            break

            file_size = 0
            if final_path and os.path.exists(final_path):
                try:
                    file_size = os.path.getsize(final_path)
                except OSError:
                    file_size = 0

            result_data = {
                "title": title,
                "file_path": final_path or "",
                "file_size": file_size,
                "file_size_str": format_bytes(file_size),
                "mode": self.mode,
                "format": self.video_format if self.mode == "video" else self.audio_format,
                "duration": duration,
                "url": self.url,
            }

            self.completed_signal.emit(result_data)

        except DownloadCancelled:
            self.cancelled_signal.emit()
        except Exception as e:
            if not self._is_cancelled:
                err_str = str(e)
                if "ERROR:" in err_str:
                    err_str = err_str.split("ERROR:", 1)[1].strip()
                self.error_signal.emit(err_str)
