from __future__ import annotations

from pathlib import Path

from photo_processor.infra.imaging.loaded_image import LoadedImage
from photo_processor.infra.imaging.pillow_runtime import require_pillow


def load_image(path: Path) -> LoadedImage:
    image_module, image_ops = require_pillow()
    with image_module.open(path) as source_image:
        image_format = source_image.format
        normalized = image_ops.exif_transpose(source_image)
        return LoadedImage(image=normalized.copy(), image_format=image_format)
