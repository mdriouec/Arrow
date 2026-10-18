"""
Comprehensive Unit & Integration Tests for Arrow.
Tests configuration management, formatting utilities, turbo download options generation,
vector icons rendering, and UI components in headless offscreen mode.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

# Initialize offscreen Qt application for testing
app = QApplication.instance()
if app is None:
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["QT_QPA_PLATFORMTHEME"] = ""
    app = QApplication(["test"])

from app.config import ConfigManager
from app.downloader import (
    DownloadWorker,
    clean_ansi,
    format_bytes,
    format_eta,
    format_speed,
)
from app.info_fetcher import format_duration, format_view_count
from app.ui.components import MediaPreviewWidget, DownloadProgressWidget
from app.ui.icons import IconFactory
from app.ui.main_window import MainWindow
from app.ui.styles import MAIN_STYLESHEET


class TestFormattingUtils(unittest.TestCase):
    """Test string and numeric formatters."""

    def test_format_bytes(self):
        self.assertEqual(format_bytes(0), "0 B")
        self.assertEqual(format_bytes(500), "500 B")
        self.assertEqual(format_bytes(1024), "1.0 KB")
        self.assertEqual(format_bytes(1024 * 1024 * 5.5), "5.5 MB")
        self.assertEqual(format_bytes(1024 * 1024 * 1024 * 2.3), "2.3 GB")

    def test_format_speed(self):
        self.assertEqual(format_speed(None), "-- KB/s")
        self.assertEqual(format_speed(0), "-- KB/s")
        self.assertEqual(format_speed(1024 * 1024 * 12.4), "12.4 MB/s")

    def test_format_eta(self):
        self.assertEqual(format_eta(None), "--:--")
        self.assertEqual(format_eta(45), "00:45")
        self.assertEqual(format_eta(125), "02:05")
        self.assertEqual(format_eta(3665), "01:01:05")

    def test_format_duration(self):
        self.assertEqual(format_duration(None), "Unknown")
        self.assertEqual(format_duration(195), "03:15")
        self.assertEqual(format_duration(7200), "02:00:00")

    def test_format_view_count(self):
        self.assertEqual(format_view_count(None), "")
        self.assertEqual(format_view_count(850), "850 views")
        self.assertEqual(format_view_count(45_000), "45.0K views")
        self.assertEqual(format_view_count(3_500_000), "3.5M views")
        self.assertEqual(format_view_count(1_200_000_000), "1.2B views")

    def test_clean_ansi(self):
        raw = "\x1b[0;32m100%\x1b[0m"
        self.assertEqual(clean_ansi(raw), "100%")


class TestConfigManager(unittest.TestCase):
    """Test settings persistence and download directory configuration."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        ConfigManager.CONFIG_DIR = Path(self.temp_dir) / ".config" / "arrow"
        ConfigManager.CONFIG_FILE = ConfigManager.CONFIG_DIR / "config.json"
        ConfigManager.LEGACY_DIR = Path(self.temp_dir) / ".config" / "legacy"
        ConfigManager.LEGACY_FILE = ConfigManager.LEGACY_DIR / "config.json"
        self.config = ConfigManager()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_default_values(self):
        self.assertEqual(self.config.get("media_mode"), "video")
        self.assertEqual(self.config.get("video_format"), "mp4")
        self.assertEqual(self.config.get("video_quality"), "best")
        self.assertEqual(self.config.get("audio_format"), "mp3")
        self.assertEqual(self.config.get("audio_quality"), "320")
        self.assertEqual(self.config.get("concurrent_fragments"), 8)
        self.assertTrue(self.config.get("embed_thumbnail"))
        self.assertTrue(self.config.get("embed_metadata"))
        self.assertTrue(os.path.exists(self.config.get("download_dir")))

    def test_save_and_reload(self):
        custom_dir = os.path.join(self.temp_dir, "custom_downloads")
        os.makedirs(custom_dir, exist_ok=True)
        self.config.set("media_mode", "audio")
        self.config.set("audio_format", "flac")
        self.config.set("download_dir", custom_dir)
        self.config.set("concurrent_fragments", 16)

        new_config = ConfigManager()
        self.assertEqual(new_config.get("media_mode"), "audio")
        self.assertEqual(new_config.get("audio_format"), "flac")
        self.assertEqual(new_config.get("download_dir"), custom_dir)
        self.assertEqual(new_config.get("concurrent_fragments"), 16)

    def test_history_management(self):
        item1 = {"title": "Song 1", "file_path": "/tmp/s1.mp3", "mode": "audio"}
        item2 = {"title": "Video 1", "file_path": "/tmp/v1.mp4", "mode": "video"}

        self.config.add_history(item1)
        self.config.add_history(item2)

        history = self.config.get("history")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["title"], "Video 1")  # newest first

        # Test removing a single item
        self.config.remove_history_item("/tmp/s1.mp3")
        history = self.config.get("history")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["file_path"], "/tmp/v1.mp4")

        self.config.clear_history()
        self.assertEqual(len(self.config.get("history")), 0)


class TestIconFactory(unittest.TestCase):
    """Test resolution-independent vector icons."""

    def test_render_all_icons(self):
        icons = [
            "app_logo", "download", "video", "music", "folder",
            "folder_open", "paste", "search", "clear", "cancel",
            "check", "play", "refresh", "history", "external",
            "trash", "delete"
        ]
        for name in icons:
            pixmap = IconFactory.get_pixmap(name, color="#6366f1", size=32)
            self.assertFalse(pixmap.isNull(), f"Failed rendering icon: {name}")
            self.assertEqual(pixmap.width(), 32)
            self.assertEqual(pixmap.height(), 32)


class TestDownloadWorkerOptions(unittest.TestCase):
    """Test yt-dlp option generation for highest quality video & music and turbo speed."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_highest_video_quality_options(self):
        worker = DownloadWorker(
            url="https://www.youtube.com/watch?v=example",
            download_dir=self.temp_dir,
            mode="video",
            video_quality="best",
            video_format="mp4",
            concurrent_fragments=8,
        )
        opts = worker._build_yt_dlp_options()
        self.assertEqual(opts["format"], "bestvideo+bestaudio/best")
        self.assertEqual(opts["merge_output_format"], "mp4")
        self.assertTrue(any(p.get("key") == "FFmpegMetadata" for p in opts["postprocessors"]))
        # Verify turbo performance settings
        self.assertEqual(opts["concurrent_fragment_downloads"], 8)
        self.assertEqual(opts["http_chunk_size"], 10485760)
        self.assertEqual(opts["buffersize"], 1048576)
        self.assertEqual(opts["postprocessor_args"]["ffmpeg"], ["-threads", "0"])

    def test_capped_resolution_options(self):
        worker = DownloadWorker(
            url="https://www.youtube.com/watch?v=example",
            download_dir=self.temp_dir,
            mode="video",
            video_quality="1080",
            video_format="mp4",
        )
        opts = worker._build_yt_dlp_options()
        self.assertEqual(opts["format"], "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best")

    def test_highest_audio_quality_mp3_options(self):
        worker = DownloadWorker(
            url="https://www.youtube.com/watch?v=example",
            download_dir=self.temp_dir,
            mode="audio",
            audio_format="mp3",
            audio_quality="320",
            embed_thumbnail=True,
            embed_metadata=True,
        )
        opts = worker._build_yt_dlp_options()
        self.assertEqual(opts["format"], "bestaudio/best")
        self.assertTrue(opts["writethumbnail"])

        pp_extract = next((p for p in opts["postprocessors"] if p.get("key") == "FFmpegExtractAudio"), None)
        self.assertIsNotNone(pp_extract)
        self.assertEqual(pp_extract["preferredcodec"], "mp3")
        self.assertEqual(pp_extract["preferredquality"], "320")

        self.assertTrue(any(p.get("key") == "EmbedThumbnail" for p in opts["postprocessors"]))
        self.assertTrue(any(p.get("key") == "FFmpegMetadata" for p in opts["postprocessors"]))

    def test_lossless_audio_flac_options(self):
        worker = DownloadWorker(
            url="https://www.youtube.com/watch?v=example",
            download_dir=self.temp_dir,
            mode="audio",
            audio_format="flac",
        )
        opts = worker._build_yt_dlp_options()
        pp_extract = next((p for p in opts["postprocessors"] if p.get("key") == "FFmpegExtractAudio"), None)
        self.assertIsNotNone(pp_extract)
        self.assertEqual(pp_extract["preferredcodec"], "flac")


class TestMainWindow(unittest.TestCase):
    """Test UI layout, state transitions, and user interactions."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        ConfigManager.CONFIG_DIR = Path(self.temp_dir) / ".config" / "arrow"
        ConfigManager.CONFIG_FILE = ConfigManager.CONFIG_DIR / "config.json"
        ConfigManager.LEGACY_DIR = Path(self.temp_dir) / ".config" / "legacy"
        ConfigManager.LEGACY_FILE = ConfigManager.LEGACY_DIR / "config.json"
        self.config = ConfigManager()
        self.window = MainWindow(self.config)

    def tearDown(self):
        self.window.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_window_initialization(self):
        self.assertIn("Arrow", self.window.windowTitle())
        self.assertTrue(os.path.isdir(self.window.dir_input.text()))

    def test_mode_switch_interaction(self):
        # Switch to audio mode
        self.window.audio_mode_btn.setChecked(True)
        self.assertEqual(self.window.options_stack.currentIndex(), 1)
        self.assertIn("Music", self.window.download_btn.text())

        # Switch to video mode
        self.window.video_mode_btn.setChecked(True)
        self.assertEqual(self.window.options_stack.currentIndex(), 0)
        self.assertIn("Video", self.window.download_btn.text())

    def test_directory_selection_persistence(self):
        new_dir = os.path.join(self.temp_dir, "CustomFolder")
        os.makedirs(new_dir, exist_ok=True)
        self.window.dir_input.setText(new_dir)
        self.config.set("download_dir", new_dir)

        self.assertEqual(self.config.get("download_dir"), new_dir)

    def test_preview_card_updates(self):
        info_data = {
            "title": "Stunning 4K Nature Video",
            "uploader": "Wildlife 4K",
            "duration_str": "05:20",
            "views_str": "2.4M views",
        }
        self.window.preview_card.set_info(info_data)
        self.assertIn("Nature Video", self.window.preview_card.title_label.text())
        self.assertEqual(self.window.preview_card.creator_label.text(), "Wildlife 4K")
        self.assertEqual(self.window.preview_card.duration_badge.text(), "05:20")

    def test_progress_card_workflow(self):
        progress = self.window.progress_card
        progress.start_download("Video")
        self.assertFalse(progress.isHidden())
        self.assertEqual(progress.progress_bar.value(), 0)

        progress.update_progress({
            "percent": 55.4,
            "speed_str": "18.5 MB/s",
            "downloaded_str": "55.4 MB",
            "total_str": "100.0 MB",
            "eta_str": "00:03",
            "status_text": "Downloading video stream (8x parallel)...",
        })
        self.assertEqual(progress.progress_bar.value(), 55)
        self.assertIn("18.5 MB/s", progress.speed_label.text())

        # Complete download
        sample_result = {
            "title": "Sample File",
            "file_path": "/tmp/sample.mp4",
            "file_size": 1024 * 1024 * 10,
            "file_size_str": "10.0 MB",
            "mode": "video",
            "format": "mp4",
        }
        progress.set_completed(sample_result)
        self.assertEqual(progress.progress_bar.value(), 100)
        self.assertFalse(progress.success_widget.isHidden())
        self.assertIsNotNone(progress.delete_btn)

    def test_delete_history_handlers(self):
        dummy_file = os.path.join(self.temp_dir, "dummy_media.mp4")
        with open(dummy_file, "w") as f:
            f.write("content")
        self.assertTrue(os.path.exists(dummy_file))

        item = {
            "title": "Dummy Song",
            "file_path": dummy_file,
            "mode": "audio",
            "format": "mp3",
        }
        self.config.add_history(item)
        self.assertEqual(len(self.config.get("history")), 1)

        # Test deleting from disk and history
        self.window._on_history_item_deleted(item, delete_from_disk=True)
        self.assertFalse(os.path.exists(dummy_file))
        self.assertEqual(len(self.config.get("history")), 0)

    def test_progress_delete_signal_handler(self):
        item = {
            "title": "Sample Download",
            "file_path": "/tmp/test_download.mp4",
            "mode": "video",
            "format": "mp4",
        }
        self.config.add_history(item)
        self.assertEqual(len(self.config.get("history")), 1)

        self.window._on_progress_file_deleted("/tmp/test_download.mp4")
        self.assertEqual(len(self.config.get("history")), 0)


if __name__ == "__main__":
    unittest.main()
