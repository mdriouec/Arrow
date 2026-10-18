"""
Custom UI components for Arrow.
Provides cards, media previews, progress bars, and history items.
"""

import os
from typing import Any, Dict, Optional
from PyQt6.QtCore import QPointF, QRectF, QSize, Qt, QUrl, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QDesktopServices,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from app.ui.icons import IconFactory


def make_rounded_pixmap(pixmap: QPixmap, target_w: int, target_h: int, radius: int = 8) -> QPixmap:
    """Scale and clip a pixmap to rounded corners."""
    scaled = pixmap.scaled(
        target_w,
        target_h,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation,
    )

    # Crop to exact dimensions from center
    x = (scaled.width() - target_w) // 2
    y = (scaled.height() - target_h) // 2
    cropped = scaled.copy(x, y, target_w, target_h)

    out = QPixmap(target_w, target_h)
    out.fill(Qt.GlobalColor.transparent)
    painter = QPainter(out)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    path = QPainterPath()
    path.addRoundedRect(0, 0, target_w, target_h, radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, cropped)
    painter.end()

    return out


class ModernCard(QFrame):
    """Reusable card frame with subtle rounded borders."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setProperty("class", "modern-card")
        self.setStyleSheet("""
            ModernCard {
                background-color: #161f30;
                border: 1px solid #2a374a;
                border-radius: 12px;
            }
        """)


class MediaPreviewWidget(ModernCard):
    """Interactive card previewing media details and thumbnail."""

    inspect_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(130)
        self._setup_ui()
        self.set_empty()

    def _setup_ui(self) -> None:
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(14, 12, 14, 12)
        self.layout.setSpacing(16)

        # Left: Thumbnail area
        self.thumb_container = QWidget()
        self.thumb_container.setFixedSize(160, 96)
        self.thumb_layout = QVBoxLayout(self.thumb_container)
        self.thumb_layout.setContentsMargins(0, 0, 0, 0)

        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(160, 96)
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_label.setStyleSheet("background-color: #0b0f19; border-radius: 8px;")
        self.thumb_layout.addWidget(self.thumb_label)

        self.layout.addWidget(self.thumb_container)

        # Right: Details area
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)
        self.details_layout.setContentsMargins(0, 4, 0, 4)
        self.details_layout.setSpacing(4)

        # Top row: title
        self.title_label = QLabel("No media inspected yet")
        self.title_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #f8fafc;")
        self.title_label.setWordWrap(True)
        self.details_layout.addWidget(self.title_label)

        # Middle row: creator / channel
        self.creator_label = QLabel("Enter a video or music link above")
        self.creator_label.setStyleSheet("font-size: 12px; color: #94a3b8;")
        self.details_layout.addWidget(self.creator_label)

        # Bottom row: stats & badges
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(10)

        self.duration_badge = QLabel("--:--")
        self.duration_badge.setStyleSheet("""
            background-color: #0f172a;
            color: #cbd5e1;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        """)
        self.stats_row.addWidget(self.duration_badge)

        self.views_label = QLabel("")
        self.views_label.setStyleSheet("color: #64748b; font-size: 11px;")
        self.stats_row.addWidget(self.views_label)

        self.ready_badge = QLabel("READY")
        self.ready_badge.setStyleSheet("""
            background-color: rgba(16, 185, 129, 0.2);
            color: #10b981;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 700;
        """)
        self.ready_badge.hide()
        self.stats_row.addWidget(self.ready_badge)

        self.stats_row.addStretch()
        self.details_layout.addLayout(self.stats_row)
        self.layout.addWidget(self.details_widget, 1)

    def set_empty(self) -> None:
        """Reset to empty initial state."""
        # Draw placeholder thumbnail
        pix = QPixmap(160, 96)
        pix.fill(QColor("#0f172a"))
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.drawPixmap(64, 32, IconFactory.get_pixmap("video", "#334155", 32))
        p.end()
        self.thumb_label.setPixmap(make_rounded_pixmap(pix, 160, 96, 8))

        self.title_label.setText("No media inspected yet")
        self.creator_label.setText("Paste a YouTube, Soundcloud, or media link above to inspect")
        self.duration_badge.setText("--:--")
        self.views_label.setText("")
        self.ready_badge.hide()

    def set_loading(self, url: str) -> None:
        """Set preview card to loading state."""
        pix = QPixmap(160, 96)
        pix.fill(QColor("#0f172a"))
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.drawPixmap(64, 32, IconFactory.get_pixmap("refresh", "#6366f1", 32))
        p.end()
        self.thumb_label.setPixmap(make_rounded_pixmap(pix, 160, 96, 8))

        self.title_label.setText("Inspecting media information...")
        self.creator_label.setText(f"Connecting to source...")
        self.duration_badge.setText("...")
        self.views_label.setText("")
        self.ready_badge.hide()

    def set_info(self, info: Dict[str, Any]) -> None:
        """Update with retrieved media metadata."""
        title = info.get("title", "Unknown Title")
        # Elide title if too long
        font_metrics = self.title_label.fontMetrics()
        elided = font_metrics.elidedText(title, Qt.TextElideMode.ElideRight, 360)
        self.title_label.setText(elided)
        self.title_label.setToolTip(title)

        uploader = info.get("uploader", "Unknown Artist")
        self.creator_label.setText(uploader)

        duration_str = info.get("duration_str", "")
        self.duration_badge.setText(duration_str)

        views_str = info.get("views_str", "")
        self.views_label.setText(views_str)
        self.ready_badge.show()

    def set_thumbnail(self, image_bytes: bytes) -> None:
        """Render thumbnail from raw bytes."""
        pixmap = QPixmap()
        if pixmap.loadFromData(image_bytes):
            self.thumb_label.setPixmap(make_rounded_pixmap(pixmap, 160, 96, 8))


class DownloadProgressWidget(ModernCard):
    """Card displaying live download progress, speed, ETA, and success actions."""

    cancel_requested = pyqtSignal()
    file_deleted_signal = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._last_result_data: Optional[Dict[str, Any]] = None
        self._setup_ui()
        self.hide()

    def _setup_ui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(18, 16, 18, 16)
        self.layout.setSpacing(12)

        # Top row: Status message & Cancel button
        self.header_row = QHBoxLayout()

        self.status_label = QLabel("Initializing download...")
        self.status_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #f8fafc;")
        self.header_row.addWidget(self.status_label, 1)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setIcon(IconFactory.get_icon("cancel", "#ef4444", 16))
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(239, 68, 68, 0.15);
                color: #fca5a5;
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.25);
                border-color: #ef4444;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_requested.emit)
        self.header_row.addWidget(self.cancel_btn)

        self.layout.addLayout(self.header_row)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #090d16;
                border: 1px solid #2a374a;
                border-radius: 6px;
                text-align: center;
                color: #f8fafc;
                font-weight: 600;
                font-size: 12px;
                height: 18px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #8b5cf6);
                border-radius: 5px;
            }
        """)
        self.layout.addWidget(self.progress_bar)

        # Live stats row
        self.stats_row = QHBoxLayout()

        self.speed_label = QLabel("Speed: -- KB/s")
        self.speed_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        self.stats_row.addWidget(self.speed_label)

        self.stats_row.addStretch()

        self.size_label = QLabel("Downloaded: 0 B / Unknown")
        self.size_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        self.stats_row.addWidget(self.size_label)

        self.stats_row.addStretch()

        self.eta_label = QLabel("ETA: --:--")
        self.eta_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        self.stats_row.addWidget(self.eta_label)

        self.layout.addLayout(self.stats_row)

        # Success container (hidden initially)
        self.success_widget = QWidget()
        self.success_layout = QHBoxLayout(self.success_widget)
        self.success_layout.setContentsMargins(0, 6, 0, 0)
        self.success_layout.setSpacing(10)

        self.success_badge = QLabel("✓ Download Finished!")
        self.success_badge.setStyleSheet("""
            color: #10b981;
            font-weight: 700;
            font-size: 13px;
        """)
        self.success_layout.addWidget(self.success_badge)

        self.success_layout.addStretch()

        self.open_file_btn = QPushButton("Open Media")
        self.open_file_btn.setIcon(IconFactory.get_icon("play", "#10b981", 14))
        self.open_file_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(16, 185, 129, 0.15);
                color: #6ee7b7;
                border: 1px solid rgba(16, 185, 129, 0.4);
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(16, 185, 129, 0.3);
            }
        """)
        self.open_file_btn.clicked.connect(self._open_media_file)
        self.success_layout.addWidget(self.open_file_btn)

        self.reveal_btn = QPushButton("Show in Folder")
        self.reveal_btn.setIcon(IconFactory.get_icon("folder_open", "#94a3b8", 14))
        self.reveal_btn.setStyleSheet("""
            QPushButton {
                background-color: #243042;
                color: #f1f5f9;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #334155;
            }
        """)
        self.reveal_btn.clicked.connect(self._reveal_in_folder)
        self.success_layout.addWidget(self.reveal_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setIcon(IconFactory.get_icon("trash", "#fca5a5", 14))
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(239, 68, 68, 0.14);
                color: #fca5a5;
                border: 1px solid rgba(239, 68, 68, 0.35);
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.28);
                border-color: #ef4444;
            }
        """)
        self.delete_btn.setToolTip("Delete downloaded file from computer")
        self.delete_btn.clicked.connect(self._delete_downloaded_file)
        self.success_layout.addWidget(self.delete_btn)

        self.layout.addWidget(self.success_widget)
        self.success_widget.hide()

    def start_download(self, mode_title: str) -> None:
        """Prepare UI for an active download."""
        self._last_result_data = None
        self.show()
        self.cancel_btn.show()
        self.success_widget.hide()
        self.open_file_btn.setEnabled(True)
        self.reveal_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Starting {mode_title}...")
        self.speed_label.setText("Speed: Connecting...")
        self.size_label.setText("Downloaded: 0 B")
        self.eta_label.setText("ETA: Calculating...")

    def update_progress(self, data: Dict[str, Any]) -> None:
        """Update live progress statistics."""
        pct = int(data.get("percent", 0))
        self.progress_bar.setValue(pct)
        self.speed_label.setText(f"Speed: {data.get('speed_str', '-- KB/s')}")
        self.size_label.setText(f"Size: {data.get('downloaded_str', '0 B')} / {data.get('total_str', 'Unknown')}")
        self.eta_label.setText(f"ETA: {data.get('eta_str', '--:--')}")
        if data.get("status_text"):
            self.status_label.setText(data["status_text"])

    def update_status(self, text: str) -> None:
        """Update general status text."""
        self.status_label.setText(text)

    def set_completed(self, result_data: Dict[str, Any]) -> None:
        """Handle download completion."""
        self._last_result_data = result_data
        self.progress_bar.setValue(100)
        self.cancel_btn.hide()
        self.status_label.setText("Processing finished!")
        self.speed_label.setText("Speed: Done")
        self.eta_label.setText("ETA: Complete")
        self.open_file_btn.setEnabled(True)
        self.reveal_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.success_widget.show()

    def set_cancelled(self) -> None:
        """Handle download cancellation."""
        self.cancel_btn.hide()
        self.status_label.setText("Download cancelled.")
        self.speed_label.setText("")
        self.eta_label.setText("")

    def set_error(self, err_text: str) -> None:
        """Handle download error state."""
        self.cancel_btn.hide()
        self.status_label.setText(f"Error: {err_text}")
        self.status_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #ef4444;")

    def _open_media_file(self) -> None:
        if self._last_result_data and self._last_result_data.get("file_path"):
            path = self._last_result_data["file_path"]
            if os.path.exists(path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def _reveal_in_folder(self) -> None:
        if self._last_result_data and self._last_result_data.get("file_path"):
            path = self._last_result_data["file_path"]
            folder = os.path.dirname(path)
            if os.path.exists(folder):
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def _delete_downloaded_file(self) -> None:
        """Prompt to delete downloaded media file permanently from disk."""
        if not self._last_result_data or not self._last_result_data.get("file_path"):
            return
        path = self._last_result_data["file_path"]
        reply = QMessageBox.question(
            self,
            "Delete Downloaded File",
            f"Are you sure you want to permanently delete this downloaded file from your disk?\n\n{os.path.basename(path)}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.exists(path):
                    os.remove(path)
                self.status_label.setText("File permanently deleted from disk.")
                self.open_file_btn.setEnabled(False)
                self.reveal_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
                self.file_deleted_signal.emit(path)
            except Exception as e:
                QMessageBox.warning(self, "Delete Error", f"Could not delete file: {e}")


class RecentDownloadsWidget(ModernCard):
    """History panel displaying recently downloaded items with play, folder, and delete options."""

    delete_requested = pyqtSignal(dict, bool)  # (item, delete_from_disk)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 12, 14, 12)
        self.layout.setSpacing(10)

        # Header
        header = QHBoxLayout()
        title = QLabel("Recent Downloads")
        title.setStyleSheet("font-size: 13px; font-weight: 700; color: #cbd5e1;")
        header.addWidget(title)

        header.addStretch()

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #64748b;
                border: none;
                font-size: 11px;
                padding: 2px 6px;
            }
            QPushButton:hover {
                color: #ef4444;
            }
        """)
        header.addWidget(self.clear_btn)
        self.layout.addLayout(header)

        # Scrollable list
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(120)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(6)

        self.empty_label = QLabel("No downloads yet")
        self.empty_label.setStyleSheet("color: #64748b; font-size: 12px; font-style: italic;")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.list_layout.addWidget(self.empty_label)

        self.scroll_area.setWidget(self.list_container)
        self.layout.addWidget(self.scroll_area)

    def populate(self, history: list) -> None:
        """Populate history rows."""
        # Clear existing
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not history:
            self.empty_label = QLabel("No downloads yet")
            self.empty_label.setStyleSheet("color: #64748b; font-size: 12px; font-style: italic;")
            self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.addWidget(self.empty_label)
            return

        for item in history:
            row = QFrame()
            row.setStyleSheet("""
                QFrame {
                    background-color: #0f172a;
                    border: 1px solid #243042;
                    border-radius: 6px;
                    padding: 4px 8px;
                }
            """)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(6, 4, 6, 4)
            row_layout.setSpacing(8)

            # Icon
            is_audio = item.get("mode") == "audio"
            icon_name = "music" if is_audio else "video"
            icon_lbl = QLabel()
            icon_lbl.setPixmap(IconFactory.get_pixmap(icon_name, "#8b5cf6" if is_audio else "#6366f1", 16))
            row_layout.addWidget(icon_lbl)

            # Title
            title_text = item.get("title", "Unknown")
            title_lbl = QLabel(title_text)
            title_lbl.setStyleSheet("font-size: 12px; color: #f1f5f9; font-weight: 500;")
            title_lbl.setToolTip(title_text)
            row_layout.addWidget(title_lbl, 1)

            # Format & Size badge
            fmt = (item.get("format") or "").upper()
            size_str = item.get("file_size_str", "")
            badge_text = f"{fmt} • {size_str}" if size_str else fmt
            badge_lbl = QLabel(badge_text)
            badge_lbl.setStyleSheet("font-size: 11px; color: #94a3b8;")
            row_layout.addWidget(badge_lbl)

            # Play button
            file_path = item.get("file_path", "")
            if file_path and os.path.exists(file_path):
                play_btn = QPushButton()
                play_btn.setIcon(IconFactory.get_icon("play", "#10b981", 12))
                play_btn.setFixedSize(24, 24)
                play_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1e293b;
                        border: 1px solid #334155;
                        border-radius: 4px;
                        padding: 0;
                    }
                    QPushButton:hover {
                        background-color: #334155;
                    }
                """)
                play_btn.setToolTip("Play media")
                play_btn.clicked.connect(lambda checked, p=file_path: QDesktopServices.openUrl(QUrl.fromLocalFile(p)))
                row_layout.addWidget(play_btn)

                # Open folder button
                folder_btn = QPushButton()
                folder_btn.setIcon(IconFactory.get_icon("folder_open", "#cbd5e1", 12))
                folder_btn.setFixedSize(24, 24)
                folder_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1e293b;
                        border: 1px solid #334155;
                        border-radius: 4px;
                        padding: 0;
                    }
                    QPushButton:hover {
                        background-color: #334155;
                    }
                """)
                folder_btn.setToolTip("Show in folder")
                folder_btn.clicked.connect(lambda checked, p=file_path: QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(p))))
                row_layout.addWidget(folder_btn)

            # Delete button (always available to delete file from disk or remove from list)
            del_btn = QPushButton()
            del_btn.setIcon(IconFactory.get_icon("trash", "#f87171", 12))
            del_btn.setFixedSize(24, 24)
            del_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b;
                    border: 1px solid #334155;
                    border-radius: 4px;
                    padding: 0;
                }
                QPushButton:hover {
                    background-color: rgba(239, 68, 68, 0.28);
                    border-color: #ef4444;
                }
            """)
            del_btn.setToolTip("Delete this file or remove from history")
            del_btn.clicked.connect(lambda checked, it=item: self._on_delete_item_clicked(it))
            row_layout.addWidget(del_btn)

            self.list_layout.addWidget(row)

    def _on_delete_item_clicked(self, item: Dict[str, Any]) -> None:
        """Prompt user with delete options: delete from disk vs remove from history."""
        file_path = item.get("file_path", "")
        title = item.get("title", "this item")
        file_exists = bool(file_path and os.path.exists(file_path))

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Delete Options")
        msg_box.setText(f"Choose a delete option for:\n\n\"{title}\"")

        del_disk_btn = None
        if file_exists:
            del_disk_btn = msg_box.addButton("Delete File from Disk", QMessageBox.ButtonRole.DestructiveRole)

        remove_list_btn = msg_box.addButton("Remove from List Only", QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton(QMessageBox.StandardButton.Cancel)

        msg_box.exec()
        clicked = msg_box.clickedButton()

        if del_disk_btn and clicked == del_disk_btn:
            self.delete_requested.emit(item, True)
        elif clicked == remove_list_btn:
            self.delete_requested.emit(item, False)

