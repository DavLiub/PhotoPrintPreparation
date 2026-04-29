from __future__ import annotations

from pathlib import Path

from photo_processor.infra.imaging.pillow_runtime import require_pillow


def load_image(path: Path):
    image_module, image_ops = require_pillow()
    with image_module.open(path) as source_image:
        normalized = image_ops.exif_transpose(source_image)
        return normalized.copy()

