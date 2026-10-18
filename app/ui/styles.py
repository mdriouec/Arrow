"""
Modern Dark Theme stylesheet and color palettes for Arrow.
Inspired by modern GNOME Libadwaita and contemporary dark desktop aesthetics.
"""

PALETTE = {
    "bg_base": "#0b0f19",
    "bg_surface": "#161f30",
    "bg_elevated": "#1e293b",
    "bg_input": "#090d16",
    "border_subtle": "#2a374a",
    "border_focus": "#6366f1",
    "accent_primary": "#6366f1",
    "accent_secondary": "#8b5cf6",
    "accent_hover": "#4f46e5",
    "accent_success": "#10b981",
    "accent_danger": "#ef4444",
    "accent_warning": "#f59e0b",
    "text_primary": "#f8fafc",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
}

MAIN_STYLESHEET = """
/* Global Window & Typography */
QMainWindow, QDialog, QWidget#centralWidget {
    background-color: #0b0f19;
    color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Cantarell", "Ubuntu", "Segoe UI", "Inter", Roboto, sans-serif;
    font-size: 13px;
}

QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

/* Card Containers */
QFrame.modern-card {
    background-color: #161f30;
    border: 1px solid #2a374a;
    border-radius: 12px;
}

QFrame.nested-card {
    background-color: #0f172a;
    border: 1px solid #243042;
    border-radius: 8px;
}

/* Text & Labels */
QLabel {
    color: #f8fafc;
    background: transparent;
}

QLabel.title-label {
    font-size: 18px;
    font-weight: 700;
    color: #ffffff;
}

QLabel.section-header {
    font-size: 13px;
    font-weight: 600;
    color: #94a3b8;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

QLabel.media-title {
    font-size: 15px;
    font-weight: 600;
    color: #f8fafc;
}

QLabel.media-meta {
    font-size: 12px;
    color: #94a3b8;
}

QLabel.stat-value {
    font-size: 13px;
    font-weight: 600;
    color: #f8fafc;
}

QLabel.stat-label {
    font-size: 11px;
    color: #64748b;
    text-transform: uppercase;
}

/* Line Edits & Inputs */
QLineEdit {
    background-color: #090d16;
    color: #f8fafc;
    border: 1px solid #2a374a;
    border-radius: 8px;
    padding: 9px 14px;
    selection-background-color: #6366f1;
    selection-color: #ffffff;
    font-size: 13px;
}

QLineEdit:focus {
    border: 1px solid #6366f1;
    background-color: #0d1320;
}

QLineEdit:hover {
    border: 1px solid #3b4c66;
}

/* Combo Boxes */
QComboBox {
    background-color: #090d16;
    color: #f8fafc;
    border: 1px solid #2a374a;
    border-radius: 8px;
    padding: 8px 12px;
    min-height: 20px;
    font-size: 13px;
}

QComboBox:hover {
    border: 1px solid #3b4c66;
}

QComboBox:focus {
    border: 1px solid #6366f1;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 26px;
    border-left: 1px solid #2a374a;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}

QComboBox::down-arrow {
    image: none;
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #94a3b8;
    margin-right: 4px;
}

QComboBox QAbstractItemView {
    background-color: #161f30;
    color: #f8fafc;
    border: 1px solid #2a374a;
    border-radius: 8px;
    padding: 4px;
    selection-background-color: #24334d;
    selection-color: #ffffff;
    outline: none;
}

/* Buttons */
QPushButton {
    background-color: #243042;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #2f3e55;
    border-color: #475569;
}

QPushButton:pressed {
    background-color: #1e2837;
}

QPushButton:disabled {
    background-color: #161f2e;
    color: #475569;
    border-color: #243042;
}

/* Primary Hero Download Button */
QPushButton#primaryDownloadBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #8b5cf6);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-size: 15px;
    font-weight: 700;
}

QPushButton#primaryDownloadBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7577f8, stop:1 #9d74f8);
}

QPushButton#primaryDownloadBtn:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f46e5, stop:1 #7c3aed);
}

QPushButton#primaryDownloadBtn:disabled {
    background: #1e293b;
    color: #64748b;
    border: 1px solid #334155;
}

/* Danger / Cancel Button */
QPushButton.danger-btn {
    background-color: #7f1d1d;
    color: #fecaca;
    border: 1px solid #991b1b;
}

QPushButton.danger-btn:hover {
    background-color: #991b1b;
    border-color: #b91c1c;
}

QPushButton.danger-btn:pressed {
    background-color: #611515;
}

/* Success Button */
QPushButton.success-btn {
    background-color: #064e3b;
    color: #a7f3d0;
    border: 1px solid #047857;
}

QPushButton.success-btn:hover {
    background-color: #047857;
}

/* Segmented Mode Button */
QPushButton.segmented-btn {
    background-color: #0f172a;
    color: #94a3b8;
    border: 1px solid #2a374a;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.segmented-btn:hover {
    color: #f8fafc;
    background-color: #172134;
}

QPushButton.segmented-btn:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #8b5cf6);
    color: #ffffff;
    border: 1px solid #8b5cf6;
}

/* Progress Bar */
QProgressBar {
    background-color: #090d16;
    border: 1px solid #2a374a;
    border-radius: 6px;
    text-align: center;
    color: #f8fafc;
    font-weight: 600;
    font-size: 12px;
    height: 14px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #10b981);
    border-radius: 5px;
}

/* Checkbox */
QCheckBox {
    color: #cbd5e1;
    font-size: 13px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #334155;
    background-color: #090d16;
}

QCheckBox::indicator:hover {
    border-color: #6366f1;
}

QCheckBox::indicator:checked {
    background-color: #6366f1;
    border-color: #6366f1;
    image: none;
}

/* Modern Scrollbars */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #2a374a;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #3b4c66;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
    border: none;
    height: 0px;
}

/* Status Pill Badges */
QFrame.pill-badge-emerald {
    background-color: rgba(16, 185, 129, 0.15);
    border: 1px solid #059669;
    border-radius: 12px;
}

QFrame.pill-badge-indigo {
    background-color: rgba(99, 102, 241, 0.15);
    border: 1px solid #6366f1;
    border-radius: 12px;
}

QToolTip {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 12px;
}
"""

