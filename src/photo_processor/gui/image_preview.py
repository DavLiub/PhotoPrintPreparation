from __future__ import annotations

from io import BytesIO


def pil_image_to_qpixmap(image):
    try:
        from PySide6.QtCore import QByteArray
        from PySide6.QtGui import QPixmap
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise RuntimeError("PySide6 is required to construct preview pixmaps.") from exc

    buffer = BytesIO()
    preview = image.convert("RGBA") if image.mode not in {"RGB", "RGBA"} else image
    preview.save(buffer, format="PNG")
    pixmap = QPixmap()
    pixmap.loadFromData(QByteArray(buffer.getvalue()), "PNG")
    return pixmap
