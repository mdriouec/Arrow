"""
Main Application Window for Arrow.
Provides an elegant, modern dark UI for downloading video and music with the highest quality.
"""

import os
from pathlib import Path
from typing import Optional
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import (
    QCloseEvent,
    QDesktopServices,
    QGuiApplication,
    QIcon,
)
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.config import ConfigManager
from app.downloader import DownloadWorker
from app.info_fetcher import InfoFetchWorker
from app.ui.components import (
    DownloadProgressWidget,
    MediaPreviewWidget,
    ModernCard,
    RecentDownloadsWidget,
)
from app.ui.icons import IconFactory
from app.ui.styles import MAIN_STYLESHEET


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, config: ConfigManager) -> None:
        super().__init__()
        self.config = config
        self.download_worker: Optional[DownloadWorker] = None
        self.info_worker: Optional[InfoFetchWorker] = None

        self.setWindowTitle("Arrow — High-Speed Video & Music Downloader")
        self.setWindowIcon(IconFactory.get_icon("app_logo", size=48))
        self.resize(780, 840)
        self.setMinimumSize(680, 600)

        self._setup_ui()
        self._load_saved_preferences()

    def _setup_ui(self) -> None:
        # Central scrollable container
        central_widget = QWidget(self)
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Scroll area for clean responsive layout
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        root_layout.addWidget(scroll_area)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(24, 20, 24, 24)
        scroll_layout.setSpacing(16)
        scroll_area.setWidget(scroll_content)

        # 1. Header Bar
        scroll_layout.addLayout(self._create_header())

        # 2. URL Input Card
        scroll_layout.addWidget(self._create_url_card())

        # 3. Media Preview Card
        self.preview_card = MediaPreviewWidget()
        scroll_layout.addWidget(self.preview_card)

        # 4. Mode & Quality Settings Card
        scroll_layout.addWidget(self._create_options_card())

        # 5. Download Directory Card
        scroll_layout.addWidget(self._create_directory_card())

        # 6. Action Button & Progress Card
        self.download_btn = QPushButton("Download Best Video (MP4)")
        self.download_btn.setObjectName("primaryDownloadBtn")
        self.download_btn.setIcon(IconFactory.get_icon("download", "#ffffff", 20))
        self.download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_btn.setFixedHeight(48)
        self.download_btn.clicked.connect(self._start_download)
        scroll_layout.addWidget(self.download_btn)

        self.progress_card = DownloadProgressWidget()
        self.progress_card.cancel_requested.connect(self._cancel_download)
        self.progress_card.file_deleted_signal.connect(self._on_progress_file_deleted)
        scroll_layout.addWidget(self.progress_card)

        # 7. Recent Downloads Tray
        self.history_card = RecentDownloadsWidget()
        self.history_card.clear_btn.clicked.connect(self._clear_history)
        self.history_card.delete_requested.connect(self._on_history_item_deleted)
        scroll_layout.addWidget(self.history_card)

        # Populate history
        self.history_card.populate(self.config.get("history", []))

    def _create_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(14)

        # Logo
        logo_lbl = QLabel()
        logo_lbl.setPixmap(IconFactory.get_pixmap("app_logo", size=42))
        header.addWidget(logo_lbl)

        # Title and subtitle
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        title_lbl = QLabel("Arrow")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px;")
        title_box.addWidget(title_lbl)

        sub_lbl = QLabel("High-Speed Video & Music Downloader for Linux")
        sub_lbl.setStyleSheet("font-size: 12px; color: #94a3b8;")
        title_box.addWidget(sub_lbl)

        header.addLayout(title_box)
        header.addStretch()

        # Turbo Engine & FFmpeg status badge
        turbo_badge = QFrame()
        turbo_badge.setStyleSheet("""
            QFrame {
                background-color: rgba(99, 102, 241, 0.14);
                border: 1px solid rgba(99, 102, 241, 0.35);
                border-radius: 14px;
                padding: 4px 10px;
            }
        """)
        turbo_layout = QHBoxLayout(turbo_badge)
        turbo_layout.setContentsMargins(6, 4, 6, 4)
        turbo_layout.setSpacing(4)
        turbo_txt = QLabel("⚡ 8x Turbo Engine")
        turbo_txt.setStyleSheet("color: #a5b4fc; font-size: 11px; font-weight: 700;")
        turbo_layout.addWidget(turbo_txt)
        header.addWidget(turbo_badge)

        badge = QFrame()
        badge.setStyleSheet("""
            QFrame {
                background-color: rgba(16, 185, 129, 0.12);
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 14px;
                padding: 4px 10px;
            }
        """)
        badge_layout = QHBoxLayout(badge)
        badge_layout.setContentsMargins(6, 4, 6, 4)
        badge_layout.setSpacing(6)

        dot = QLabel("●")
        dot.setStyleSheet("color: #10b981; font-size: 11px;")
        badge_layout.addWidget(dot)

        badge_txt = QLabel("FFmpeg Ready")
        badge_txt.setStyleSheet("color: #a7f3d0; font-size: 11px; font-weight: 600;")
        badge_layout.addWidget(badge_txt)

        header.addWidget(badge)
        return header

    def _create_url_card(self) -> ModernCard:
        card = ModernCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        label_row = QHBoxLayout()
        lbl = QLabel("MEDIA URL")
        lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #94a3b8; letter-spacing: 0.5px;")
        label_row.addWidget(lbl)
        label_row.addStretch()

        layout.addLayout(label_row)

        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube, Vimeo, Soundcloud, or media link here...")
        self.url_input.returnPressed.connect(self._inspect_url)
        self.url_input.textChanged.connect(self._on_url_text_changed)
        input_row.addWidget(self.url_input, 1)

        # Paste button
        self.paste_btn = QPushButton("Paste")
        self.paste_btn.setIcon(IconFactory.get_icon("paste", "#cbd5e1", 16))
        self.paste_btn.setToolTip("Paste link from clipboard")
        self.paste_btn.clicked.connect(self._paste_clipboard)
        input_row.addWidget(self.paste_btn)

        # Inspect button
        self.inspect_btn = QPushButton("Inspect")
        self.inspect_btn.setIcon(IconFactory.get_icon("search", "#cbd5e1", 16))
        self.inspect_btn.setToolTip("Fetch media title, details, and preview")
        self.inspect_btn.clicked.connect(self._inspect_url)
        input_row.addWidget(self.inspect_btn)

        # Clear button
        self.clear_btn = QPushButton()
        self.clear_btn.setIcon(IconFactory.get_icon("clear", "#94a3b8", 16))
        self.clear_btn.setToolTip("Clear URL")
        self.clear_btn.setFixedSize(36, 36)
        self.clear_btn.clicked.connect(self._clear_url)
        input_row.addWidget(self.clear_btn)

        layout.addLayout(input_row)
        return card

    def _create_options_card(self) -> ModernCard:
        card = ModernCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)

        # Section title
        sec_title = QLabel("DOWNLOAD MODE & QUALITY")
        sec_title.setStyleSheet("font-size: 11px; font-weight: 700; color: #94a3b8; letter-spacing: 0.5px;")
        layout.addWidget(sec_title)

        # Segmented Mode Switch: [ 🎬 Video ] / [ 🎵 Music ]
        mode_btn_row = QHBoxLayout()
        mode_btn_row.setSpacing(10)

        self.mode_group = QButtonGroup(self)

        self.video_mode_btn = QPushButton("  Video (Highest Quality)")
        self.video_mode_btn.setIcon(IconFactory.get_icon("video", "#ffffff", 18))
        self.video_mode_btn.setCheckable(True)
        self.video_mode_btn.setProperty("class", "segmented-btn")
        self.video_mode_btn.setFixedHeight(40)
        self.mode_group.addButton(self.video_mode_btn)
        mode_btn_row.addWidget(self.video_mode_btn, 1)

        self.audio_mode_btn = QPushButton("  Music / Audio Only")
        self.audio_mode_btn.setIcon(IconFactory.get_icon("music", "#ffffff", 18))
        self.audio_mode_btn.setCheckable(True)
        self.audio_mode_btn.setProperty("class", "segmented-btn")
        self.audio_mode_btn.setFixedHeight(40)
        self.mode_group.addButton(self.audio_mode_btn)
        mode_btn_row.addWidget(self.audio_mode_btn, 1)

        self.video_mode_btn.toggled.connect(self._on_mode_toggled)
        layout.addLayout(mode_btn_row)

        # Stacked options container
        self.options_stack = QStackedWidget()

        # Page 0: Video Options
        video_page = QWidget()
        v_layout = QGridLayout(video_page)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setHorizontalSpacing(14)
        v_layout.setVerticalSpacing(8)

        v_res_lbl = QLabel("Maximum Resolution:")
        v_res_lbl.setStyleSheet("color: #cbd5e1; font-weight: 500;")
        v_layout.addWidget(v_res_lbl, 0, 0)

        self.video_res_combo = QComboBox()
        self.video_res_combo.addItem("★ Best Available (Combines Highest Video + Audio)", "best")
        self.video_res_combo.addItem("4K UHD (2160p)", "2160")
        self.video_res_combo.addItem("2K QHD (1440p)", "1440")
        self.video_res_combo.addItem("Full HD (1080p)", "1080")
        self.video_res_combo.addItem("HD (720p)", "720")
        self.video_res_combo.currentIndexChanged.connect(self._save_preferences)
        v_layout.addWidget(self.video_res_combo, 0, 1)

        v_fmt_lbl = QLabel("Container Format:")
        v_fmt_lbl.setStyleSheet("color: #cbd5e1; font-weight: 500;")
        v_layout.addWidget(v_fmt_lbl, 1, 0)

        self.video_fmt_combo = QComboBox()
        self.video_fmt_combo.addItem("MP4 (Universal standard, best compatibility)", "mp4")
        self.video_fmt_combo.addItem("MKV (Matroska high efficiency container)", "mkv")
        self.video_fmt_combo.addItem("WEBM (Open Web format)", "webm")
        self.video_fmt_combo.currentIndexChanged.connect(self._save_preferences)
        v_layout.addWidget(self.video_fmt_combo, 1, 1)

        self.options_stack.addWidget(video_page)

        # Page 1: Audio / Music Options
        audio_page = QWidget()
        a_layout = QGridLayout(audio_page)
        a_layout.setContentsMargins(0, 0, 0, 0)
        a_layout.setHorizontalSpacing(14)
        a_layout.setVerticalSpacing(8)

        a_fmt_lbl = QLabel("Audio Format:")
        a_fmt_lbl.setStyleSheet("color: #cbd5e1; font-weight: 500;")
        a_layout.addWidget(a_fmt_lbl, 0, 0)

        self.audio_fmt_combo = QComboBox()
        self.audio_fmt_combo.addItem("★ MP3 - 320 kbps (Highest Quality & Compatible)", "mp3")
        self.audio_fmt_combo.addItem("FLAC - Lossless Studio Master Quality", "flac")
        self.audio_fmt_combo.addItem("M4A - High Bitrate AAC Audio", "m4a")
        self.audio_fmt_combo.addItem("OPUS - Ultra High-Fidelity Audio", "opus")
        self.audio_fmt_combo.addItem("Original Stream (Pure stream copy, no transcode)", "best")
        self.audio_fmt_combo.currentIndexChanged.connect(self._on_audio_format_changed)
        a_layout.addWidget(self.audio_fmt_combo, 0, 1)

        self.audio_bitrate_lbl = QLabel("MP3 Bitrate:")
        self.audio_bitrate_lbl.setStyleSheet("color: #cbd5e1; font-weight: 500;")
        a_layout.addWidget(self.audio_bitrate_lbl, 1, 0)

        self.audio_bitrate_combo = QComboBox()
        self.audio_bitrate_combo.addItem("320 kbps (CBR Best Studio Audio)", "320")
        self.audio_bitrate_combo.addItem("256 kbps (High Quality)", "256")
        self.audio_bitrate_combo.addItem("192 kbps (Standard Quality)", "192")
        self.audio_bitrate_combo.currentIndexChanged.connect(self._save_preferences)
        a_layout.addWidget(self.audio_bitrate_combo, 1, 1)

        # Checkboxes for audio metadata & album art
        meta_row = QHBoxLayout()
        self.embed_thumb_chk = QCheckBox("Embed High-Resolution Album Cover Art")
        self.embed_thumb_chk.setChecked(True)
        self.embed_thumb_chk.toggled.connect(self._save_preferences)
        meta_row.addWidget(self.embed_thumb_chk)

        self.embed_meta_chk = QCheckBox("Embed Artist, Title & ID3 Tags")
        self.embed_meta_chk.setChecked(True)
        self.embed_meta_chk.toggled.connect(self._save_preferences)
        meta_row.addWidget(self.embed_meta_chk)

        a_layout.addLayout(meta_row, 2, 0, 1, 2)

        self.options_stack.addWidget(audio_page)
        layout.addWidget(self.options_stack)

        return card

    def _create_directory_card(self) -> ModernCard:
        card = ModernCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        lbl = QLabel("DOWNLOAD DESTINATION FOLDER")
        lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #94a3b8; letter-spacing: 0.5px;")
        layout.addWidget(lbl)

        row = QHBoxLayout()
        row.setSpacing(8)

        self.dir_input = QLineEdit()
        self.dir_input.setText(self.config.get("download_dir", ""))
        self.dir_input.setReadOnly(True)
        self.dir_input.setStyleSheet("""
            QLineEdit {
                background-color: #090d16;
                color: #e2e8f0;
                font-family: monospace;
                font-size: 12px;
            }
        """)
        row.addWidget(self.dir_input, 1)

        # Browse button
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setIcon(IconFactory.get_icon("folder", "#cbd5e1", 16))
        self.browse_btn.setToolTip("Select download directory")
        self.browse_btn.clicked.connect(self._browse_directory)
        row.addWidget(self.browse_btn)

        # Open folder in Linux file manager
        self.open_folder_btn = QPushButton("Open")
        self.open_folder_btn.setIcon(IconFactory.get_icon("folder_open", "#cbd5e1", 16))
        self.open_folder_btn.setToolTip("Open folder in file manager")
        self.open_folder_btn.clicked.connect(self._open_current_directory)
        row.addWidget(self.open_folder_btn)

        layout.addLayout(row)
        return card

    def _load_saved_preferences(self) -> None:
        """Apply loaded configuration values to UI."""
        # Mode
        mode = self.config.get("media_mode", "video")
        if mode == "audio":
            self.audio_mode_btn.setChecked(True)
            self.options_stack.setCurrentIndex(1)
        else:
            self.video_mode_btn.setChecked(True)
            self.options_stack.setCurrentIndex(0)

        # Video quality
        vid_q = self.config.get("video_quality", "best")
        idx = self.video_res_combo.findData(vid_q)
        if idx != -1:
            self.video_res_combo.setCurrentIndex(idx)

        # Video format
        vid_f = self.config.get("video_format", "mp4")
        idx = self.video_fmt_combo.findData(vid_f)
        if idx != -1:
            self.video_fmt_combo.setCurrentIndex(idx)

        # Audio format
        aud_f = self.config.get("audio_format", "mp3")
        idx = self.audio_fmt_combo.findData(aud_f)
        if idx != -1:
            self.audio_fmt_combo.setCurrentIndex(idx)

        # Audio quality
        aud_q = self.config.get("audio_quality", "320")
        idx = self.audio_bitrate_combo.findData(aud_q)
        if idx != -1:
            self.audio_bitrate_combo.setCurrentIndex(idx)

        self.embed_thumb_chk.setChecked(self.config.get("embed_thumbnail", True))
        self.embed_meta_chk.setChecked(self.config.get("embed_metadata", True))

        self._update_download_button_label()

    def _save_preferences(self) -> None:
        """Save UI values back to persistent config."""
        mode = "audio" if self.audio_mode_btn.isChecked() else "video"
        self.config.set("media_mode", mode, auto_save=False)
        self.config.set("video_quality", self.video_res_combo.currentData(), auto_save=False)
        self.config.set("video_format", self.video_fmt_combo.currentData(), auto_save=False)
        self.config.set("audio_format", self.audio_fmt_combo.currentData(), auto_save=False)
        self.config.set("audio_quality", self.audio_bitrate_combo.currentData(), auto_save=False)
        self.config.set("embed_thumbnail", self.embed_thumb_chk.isChecked(), auto_save=False)
        self.config.set("embed_metadata", self.embed_meta_chk.isChecked(), auto_save=False)
        self.config.save()

        self._update_download_button_label()

    def _on_mode_toggled(self) -> None:
        """Handle toggle between video and audio modes."""
        is_audio = self.audio_mode_btn.isChecked()
        self.options_stack.setCurrentIndex(1 if is_audio else 0)
        self._save_preferences()

    def _on_audio_format_changed(self) -> None:
        """Enable or disable bitrate dropdown depending on chosen audio codec."""
        fmt = self.audio_fmt_combo.currentData()
        is_mp3 = fmt == "mp3"
        self.audio_bitrate_lbl.setVisible(is_mp3)
        self.audio_bitrate_combo.setVisible(is_mp3)
        self._save_preferences()

    def _update_download_button_label(self) -> None:
        """Update download button caption and icon based on mode."""
        if self.audio_mode_btn.isChecked():
            fmt = (self.audio_fmt_combo.currentData() or "mp3").upper()
            if fmt == "MP3":
                kbps = self.audio_bitrate_combo.currentData() or "320"
                self.download_btn.setText(f"Download Music ({fmt} {kbps}k)")
            elif fmt == "FLAC":
                self.download_btn.setText("Download Lossless Audio (FLAC)")
            elif fmt == "BEST":
                self.download_btn.setText("Download Original Audio Stream")
            else:
                self.download_btn.setText(f"Download Audio ({fmt})")
            self.download_btn.setIcon(IconFactory.get_icon("music", "#ffffff", 20))
        else:
            fmt = (self.video_fmt_combo.currentData() or "mp4").upper()
            res = self.video_res_combo.currentData()
            res_str = "Best" if res == "best" else f"{res}p"
            self.download_btn.setText(f"Download Video ({res_str} {fmt})")
            self.download_btn.setIcon(IconFactory.get_icon("download", "#ffffff", 20))

    def _browse_directory(self) -> None:
        """Prompt user to choose a directory with native Linux folder picker."""
        current_dir = self.dir_input.text() or str(Path.home())
        chosen_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Storage Directory for Downloads",
            current_dir,
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks,
        )
        if chosen_dir and os.path.isdir(chosen_dir):
            self.dir_input.setText(chosen_dir)
            self.config.set("download_dir", chosen_dir)

    def _open_current_directory(self) -> None:
        """Open the currently selected download directory in file manager."""
        folder = self.dir_input.text()
        if folder and os.path.isdir(folder):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def _paste_clipboard(self) -> None:
        """Paste URL from clipboard and inspect."""
        clipboard = QGuiApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.url_input.setText(text)
            self._inspect_url()

    def _clear_url(self) -> None:
        """Clear URL and reset preview."""
        self.url_input.clear()
        self.preview_card.set_empty()

    def _on_url_text_changed(self, text: str) -> None:
        """Auto inspect if user pastes a full http(s) URL."""
        t = text.strip()
        if t.startswith(("http://", "https://")) and len(t) > 15:
            # Only auto-inspect if not currently inspecting
            if not self.info_worker or not self.info_worker.isRunning():
                pass  # Keep ready for Inspect click or Enter

    def _inspect_url(self) -> None:
        """Fetch media metadata and thumbnail preview."""
        url = self.url_input.text().strip()
        if not url:
            return

        if self.info_worker and self.info_worker.isRunning():
            self.info_worker.cancel()
            self.info_worker.wait()

        self.preview_card.set_loading(url)
        self.inspect_btn.setEnabled(False)

        self.info_worker = InfoFetchWorker(url)
        self.info_worker.info_loaded.connect(self._on_info_loaded)
        self.info_worker.thumbnail_loaded.connect(self.preview_card.set_thumbnail)
        self.info_worker.error_occurred.connect(self._on_info_error)
        self.info_worker.finished.connect(lambda: self.inspect_btn.setEnabled(True))
        self.info_worker.start()

    def _on_info_loaded(self, info: dict) -> None:
        """Handle successful media details retrieval."""
        self.preview_card.set_info(info)

    def _on_info_error(self, err_msg: str) -> None:
        """Handle info inspection error."""
        self.preview_card.title_label.setText("Could not inspect URL")
        self.preview_card.creator_label.setText(err_msg)

    def _start_download(self) -> None:
        """Initiate video or audio download."""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "No URL", "Please enter or paste a video or music link first.")
            return

        download_dir = self.dir_input.text().strip()
        if not download_dir or not os.path.exists(download_dir):
            QMessageBox.warning(self, "Invalid Directory", "Please select a valid folder to save your files.")
            return

        if self.download_worker and self.download_worker.isRunning():
            QMessageBox.information(self, "Download in Progress", "A download is already running. Please wait or cancel it.")
            return

        mode = "audio" if self.audio_mode_btn.isChecked() else "video"
        mode_title = "Music" if mode == "audio" else "Video"

        self.download_btn.setEnabled(False)
        self.progress_card.start_download(mode_title)

        self.download_worker = DownloadWorker(
            url=url,
            download_dir=download_dir,
            mode=mode,
            video_quality=self.video_res_combo.currentData(),
            video_format=self.video_fmt_combo.currentData(),
            audio_format=self.audio_fmt_combo.currentData(),
            audio_quality=self.audio_bitrate_combo.currentData(),
            embed_thumbnail=self.embed_thumb_chk.isChecked(),
            embed_metadata=self.embed_meta_chk.isChecked(),
            concurrent_fragments=self.config.get("concurrent_fragments", 8),
        )

        self.download_worker.progress_signal.connect(self.progress_card.update_progress)
        self.download_worker.status_signal.connect(self.progress_card.update_status)
        self.download_worker.completed_signal.connect(self._on_download_completed)
        self.download_worker.cancelled_signal.connect(self._on_download_cancelled)
        self.download_worker.error_signal.connect(self._on_download_error)
        self.download_worker.finished.connect(lambda: self.download_btn.setEnabled(True))

        self.download_worker.start()

    def _cancel_download(self) -> None:
        """Cancel active download."""
        if self.download_worker and self.download_worker.isRunning():
            self.download_worker.cancel()

    def _on_download_completed(self, result_data: dict) -> None:
        """Handle download completion."""
        self.progress_card.set_completed(result_data)
        # Add to history
        self.config.add_history(result_data)
        self.history_card.populate(self.config.get("history", []))

    def _on_download_cancelled(self) -> None:
        """Handle download cancellation."""
        self.progress_card.set_cancelled()

    def _on_download_error(self, err_msg: str) -> None:
        """Handle download error."""
        self.progress_card.set_error(err_msg)

    def _on_progress_file_deleted(self, file_path: str) -> None:
        """Remove deleted file from history and refresh history list."""
        self.config.remove_history_item(file_path)
        self.history_card.populate(self.config.get("history", []))

    def _on_history_item_deleted(self, item: dict, delete_from_disk: bool) -> None:
        """Handle item deletion from history and optionally disk."""
        file_path = item.get("file_path", "")
        if delete_from_disk and file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                QMessageBox.warning(self, "Delete Error", f"Could not delete file from disk:\n{e}")

        self.config.remove_history_item(file_path)
        self.history_card.populate(self.config.get("history", []))

    def _clear_history(self) -> None:
        """Prompt confirmation before clearing download history."""
        history = self.config.get("history", [])
        if not history:
            return
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear your download history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.config.clear_history()
            self.history_card.populate([])

    def closeEvent(self, event: QCloseEvent) -> None:
        """Ensure background threads are cleanly stopped on window close."""
        if self.download_worker and self.download_worker.isRunning():
            self.download_worker.cancel()
            self.download_worker.wait(2000)

        if self.info_worker and self.info_worker.isRunning():
            self.info_worker.cancel()
            self.info_worker.wait(1000)

        event.accept()

