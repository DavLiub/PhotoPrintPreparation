from __future__ import annotations


def require_pillow():
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise RuntimeError(
            "Pillow is required for image processing. Install project dependencies first."
        ) from exc

    return Image, ImageOps

