from __future__ import annotations

from io import BytesIO
from pathlib import Path

from photo_processor.infra.imaging.jpeg_save_result import JpegSaveResult
from photo_processor.infra.imaging.pillow_runtime import require_pillow

QUALITY_STEPS = (90, 85, 80, 75, 70)
DIMENSION_REDUCTION_FACTOR = 0.95


def save_jpeg_with_limit(image, output_path: Path, max_file_size_mb: float) -> JpegSaveResult:
    target_bytes = int(max_file_size_mb * 1024 * 1024)
    working = image.convert("RGB")
    dimension_reduced = False

    while True:
        for quality in QUALITY_STEPS:
            encoded = _encode_jpeg(working, quality)
            if len(encoded) <= target_bytes:
                output_path.write_bytes(encoded)
                return JpegSaveResult(
                    output_size=working.size,
                    file_size_bytes=len(encoded),
                    quality=quality,
                    was_dimension_reduced=dimension_reduced,
                )

        next_width = max(1, round(working.width * DIMENSION_REDUCTION_FACTOR))
        next_height = max(1, round(working.height * DIMENSION_REDUCTION_FACTOR))

        if (next_width, next_height) == working.size:
            encoded = _encode_jpeg(working, QUALITY_STEPS[-1])
            output_path.write_bytes(encoded)
            return JpegSaveResult(
                output_size=working.size,
                file_size_bytes=len(encoded),
                quality=QUALITY_STEPS[-1],
                was_dimension_reduced=dimension_reduced,
            )

        image_module, _ = require_pillow()
        resampling = getattr(image_module, "Resampling", image_module)
        working = working.resize((next_width, next_height), resample=resampling.LANCZOS)
        dimension_reduced = True


def _encode_jpeg(image, quality: int) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()
