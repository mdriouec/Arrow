"""
Vector icon generator for Arrow using QPainter.
Generates resolution-independent, crisp icons directly in memory without
relying on external fonts or system-dependent icon themes.
"""

from typing import Optional
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)


class IconFactory:
    """Creates crisp vector-based QPixmap and QIcon instances."""

    _cache = {}

    @classmethod
    def get_icon(cls, name: str, color: Optional[str] = None, size: int = 24) -> QIcon:
        """Return a QIcon for the given name, color, and size."""
        pixmap = cls.get_pixmap(name, color=color, size=size)
        return QIcon(pixmap)

    @classmethod
    def get_pixmap(cls, name: str, color: Optional[str] = None, size: int = 24) -> QPixmap:
        """Generate and cache vector pixmaps."""
        cache_key = f"{name}_{color}_{size}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        draw_color = QColor(color) if color else QColor("#cbd5e1")
        pen_width = max(1.5, size * 0.075)
        pen = QPen(draw_color, pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        s = float(size)

        if name == "app_logo":
            cls._draw_app_logo(painter, s)
        elif name == "download":
            cls._draw_download(painter, pen, s)
        elif name == "video":
            cls._draw_video(painter, pen, s)
        elif name == "music":
            cls._draw_music(painter, pen, s, draw_color)
        elif name == "folder":
            cls._draw_folder(painter, pen, s)
        elif name == "folder_open":
            cls._draw_folder_open(painter, pen, s)
        elif name == "paste":
            cls._draw_paste(painter, pen, s)
        elif name == "search":
            cls._draw_search(painter, pen, s)
        elif name == "clear":
            cls._draw_clear(painter, pen, s)
        elif name == "cancel":
            cls._draw_cancel(painter, pen, s)
        elif name == "check":
            cls._draw_check(painter, pen, s)
        elif name == "play":
            cls._draw_play(painter, s, draw_color)
        elif name == "refresh":
            cls._draw_refresh(painter, pen, s)
        elif name == "history":
            cls._draw_history(painter, pen, s)
        elif name == "external":
            cls._draw_external(painter, pen, s)
        elif name in ("trash", "delete"):
            cls._draw_trash(painter, pen, s)
        else:
            # Fallback circle
            painter.drawEllipse(QRectF(s * 0.2, s * 0.2, s * 0.6, s * 0.6))

        painter.end()
        cls._cache[cache_key] = pixmap
        return pixmap

    @staticmethod
    def _draw_app_logo(painter: QPainter, s: float) -> None:
        """Draw app icon from icon/ folder if available, with squircle rounding and fallback."""
        import os
        from pathlib import Path

        # Look for icon picture in icon/ folder or assets/
        candidates = []
        base_dir = Path(__file__).resolve().parent.parent.parent
        icon_dir = base_dir / "icon"
        if icon_dir.exists():
            for f in sorted(icon_dir.iterdir()):
                if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
                    candidates.append(str(f))

        assets_icon = base_dir / "assets" / "icon.png"
        if assets_icon.exists():
            candidates.append(str(assets_icon))

        for cand in candidates:
            img_pix = QPixmap(cand)
            if not img_pix.isNull():
                margin = s * 0.04
                rect = QRectF(margin, margin, s - 2 * margin, s - 2 * margin)

                # Clip to squircle
                clip_path = QPainterPath()
                clip_path.addRoundedRect(rect, s * 0.22, s * 0.22)

                # Center square crop from source
                iw, ih = img_pix.width(), img_pix.height()
                crop_dim = min(iw, ih)
                cx = (iw - crop_dim) // 2
                cy = int((ih - crop_dim) * 0.25)
                cropped_src = img_pix.copy(cx, max(0, cy), crop_dim, crop_dim)

                scaled = cropped_src.scaled(
                    int(rect.width()),
                    int(rect.height()),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )

                painter.save()
                painter.setClipPath(clip_path)
                painter.drawPixmap(int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height()), scaled)
                painter.restore()

                # Subtle border outline
                glow_pen = QPen(QColor(255, 255, 255, 80), max(1.0, s * 0.02))
                painter.setPen(glow_pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(rect, s * 0.22, s * 0.22)
                return

        # Fallback vector emblem
        gradient = QLinearGradient(0, 0, s, s)
        gradient.setColorAt(0.0, QColor("#3b82f6"))
        gradient.setColorAt(0.5, QColor("#6366f1"))
        gradient.setColorAt(1.0, QColor("#9333ea"))

        margin = s * 0.05
        rect = QRectF(margin, margin, s - 2 * margin, s - 2 * margin)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(rect, s * 0.22, s * 0.22)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#ffffff")))
        arrow = QPainterPath()
        arrow.moveTo(s * 0.50, s * 0.76)
        arrow.lineTo(s * 0.22, s * 0.44)
        arrow.lineTo(s * 0.35, s * 0.44)
        arrow.lineTo(s * 0.50, s * 0.60)
        arrow.lineTo(s * 0.65, s * 0.44)
        arrow.lineTo(s * 0.78, s * 0.44)
        arrow.closeSubpath()
        painter.drawPath(arrow)

    @staticmethod
    def _draw_download(painter: QPainter, pen: QPen, s: float) -> None:
        painter.setPen(pen)
        # Down arrow
        cx = s * 0.5
        painter.drawLine(QPointF(cx, s * 0.18), QPointF(cx, s * 0.64))
        painter.drawLine(QPointF(s * 0.30, s * 0.46), QPointF(cx, s * 0.64))
        painter.drawLine(QPointF(s * 0.70, s * 0.46), QPointF(cx, s * 0.64))
        # Tray
        painter.drawLine(QPointF(s * 0.20, s * 0.82), QPointF(s * 0.80, s * 0.82))

    @staticmethod
    def _draw_video(painter: QPainter, pen: QPen, s: float) -> None:
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # Screen frame
        painter.drawRoundedRect(QRectF(s * 0.16, s * 0.22, s * 0.68, s * 0.56), s * 0.1, s * 0.1)
        # Small play triangle in the center
        p = QPainterPath()
        p.moveTo(s * 0.44, s * 0.38)
        p.lineTo(s * 0.60, s * 0.50)
        p.lineTo(s * 0.44, s * 0.62)
        p.closeSubpath()
        painter.fillPath(p, pen.brush())

    @staticmethod
    def _draw_music(painter: QPainter, pen: QPen, s: float, color: QColor) -> None:
        painter.setPen(pen)
        # Note stems and beam
        painter.drawLine(QPointF(s * 0.34, s * 0.68), QPointF(s * 0.34, s * 0.26))
        painter.drawLine(QPointF(s * 0.70, s * 0.58), QPointF(s * 0.70, s * 0.18))
        painter.drawLine(QPointF(s * 0.34, s * 0.26), QPointF(s * 0.70, s * 0.18))
        # Note heads
        painter.setBrush(QBrush(color))
        painter.drawEllipse(QRectF(s * 0.20, s * 0.60, s * 0.16, s * 0.14))
        painter.drawEllipse(QRectF(s * 0.56, s * 0.50, s * 0.16, s * 0.14))

    @staticmethod
    def _draw_folder(painter: QPainter, pen: QPen, s: float) -> None:
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        path = QPainterPath()
        path.moveTo(s * 0.15, s * 0.30)
        path.lineTo(s * 0.40, s * 0.30)
        path.lineTo(s * 0.48, s * 0.40)
        path.lineTo(s * 0.85, s * 0.40)
        path.lineTo(s * 0.85, s * 0.78)
        path.lineTo(s * 0.15, s * 0.78)
        path.closeSubpath()
        painter.drawPath(path)

    @staticmethod
    def _draw_folder_open(painter: QPainter, pen: QPen, s: float) -> None:
        IconFactory._draw_folder(painter, pen, s)
        # Little arrow pointing up/right
        painter.drawLine(QPointF(s * 0.60, s * 0.22), QPointF(s * 0.82, s * 0.22))
        painter.drawLine(QPointF(s * 0.82, s * 0.22), QPointF(s * 0.82, s * 0.44))
        painter.drawLine(QPointF(s * 0.52, s * 0.52), QPointF(s * 0.82, s * 0.22))

    @staticmethod
    def _draw_paste(painter: QPainter, pen: QPen, s: float) -> None:
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # Board
        painter.drawRoundedRect(QRectF(s * 0.22, s * 0.26, s * 0.56, s * 0.62), s * 0.08, s * 0.08)
        # Clip top
        painter.drawRoundedRect(QRectF(s * 0.36, s * 0.16, s * 0.28, s * 0.14), s * 0.04, s * 0.04)
        # Content lines
        painter.drawLine(QPointF(s * 0.34, s * 0.45), QPointF(s * 0.66, s * 0.45))
        painter.drawLine(QPointF(s * 0.34, s * 0.58), QPointF(s * 0.66, s * 0.58))
        painter.drawLine(QPointF(s * 0.34, s * 0.71), QPointF(s * 0.54, s * 0.71))

    @staticmethod
    def _draw_search(painter: QPainter, pen: QPen, s: float) -> None:
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        r = s * 0.24
        painter.drawEllipse(QPointF(s * 0.42, s * 0.42), r, r)
        painter.drawLine(QPointF(s * 0.59, s * 0.59), QPointF(s * 0.82, s * 0.82))

    @staticmethod
    def _draw_clear(painter: QPainter, pen: QPen, s: float) -> None:
        painter.setPen(pen)
        margin = s * 0.28
        painter.drawLine(QPointF(margin, margin), QPointF(s - margin, s - margin))
        painter.drawLine(QPointF(s - margin, margin), QPointF(margin, s - margin))

    @staticmethod
    def _draw_cancel(painter: QPainter, pen: QPen, s: float) -> None:
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(s * 0.15, s * 0.15, s * 0.70, s * 0.70))
        m = s * 0.34
        painter.drawLine(QPointF(m, m), QPointF(s - m, s - m))
        painter.drawLine(QPointF(s - m, m), QPointF(m, s - m))

    @staticmethod
    def _draw_check(painter: QPainter, pen: QPen, s: float) -> None:
        painter.setPen(pen)
        path = QPainterPath()
        path.moveTo(s * 0.20, s * 0.52)
        path.lineTo(s * 0.42, s * 0.74)
        path.lineTo(s * 0.82, s * 0.28)
        painter.drawPath(path)

    @staticmethod
    def _draw_play(painter: QPainter, s: float, color: QColor) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        path = QPainterPath()
        path.moveTo(s * 0.28, s * 0.20)
        path.lineTo(s * 0.76, s * 0.50)
        path.lineTo(s * 0.28, s * 0.80)
        path.closeSubpath()
        painter.drawPath(path)

    @staticmethod
    def _draw_refresh(painter: QPainter, pen: QPen, s: float) -> None:
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        rect = QRectF(s * 0.20, s * 0.20, s * 0.60, s * 0.60)
        painter.drawArc(rect, 45 * 16, 270 * 16)
        # Arrowhead
        painter.drawLine(QPointF(s * 0.75, s * 0.35), QPointF(s * 0.80, s * 0.50))
        painter.drawLine(QPointF(s * 0.65, s * 0.50), QPointF(s * 0.80, s * 0.50))

    @staticmethod
    def _draw_history(painter: QPainter, pen: QPen, s: float) -> None:
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(s * 0.16, s * 0.16, s * 0.68, s * 0.68))
        cx = s * 0.5
        cy = s * 0.5
        painter.drawLine(QPointF(cx, cy), QPointF(cx, s * 0.30))
        painter.drawLine(QPointF(cx, cy), QPointF(s * 0.68, cy))

    @staticmethod
    def _draw_external(painter: QPainter, pen: QPen, s: float) -> None:
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # Arrow top-right
        painter.drawLine(QPointF(s * 0.40, s * 0.22), QPointF(s * 0.78, s * 0.22))
        painter.drawLine(QPointF(s * 0.78, s * 0.22), QPointF(s * 0.78, s * 0.60))
        painter.drawLine(QPointF(s * 0.35, s * 0.65), QPointF(s * 0.78, s * 0.22))
        # Lower frame
        path = QPainterPath()
        path.moveTo(s * 0.60, s * 0.45)
        path.lineTo(s * 0.60, s * 0.78)
        path.lineTo(s * 0.22, s * 0.78)
        path.lineTo(s * 0.22, s * 0.40)
        path.lineTo(s * 0.55, s * 0.40)
        painter.drawPath(path)

    @staticmethod
    def _draw_trash(painter: QPainter, pen: QPen, s: float) -> None:
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # Handle
        painter.drawLine(QPointF(s * 0.38, s * 0.18), QPointF(s * 0.62, s * 0.18))
        # Lid bar
        painter.drawLine(QPointF(s * 0.18, s * 0.28), QPointF(s * 0.82, s * 0.28))
        # Bin body
        bin_path = QPainterPath()
        bin_path.moveTo(s * 0.25, s * 0.28)
        bin_path.lineTo(s * 0.29, s * 0.82)
        bin_path.lineTo(s * 0.71, s * 0.82)
        bin_path.lineTo(s * 0.75, s * 0.28)
        painter.drawPath(bin_path)
        # Vertical ribs
        painter.drawLine(QPointF(s * 0.42, s * 0.40), QPointF(s * 0.42, s * 0.72))
        painter.drawLine(QPointF(s * 0.58, s * 0.40), QPointF(s * 0.58, s * 0.72))
