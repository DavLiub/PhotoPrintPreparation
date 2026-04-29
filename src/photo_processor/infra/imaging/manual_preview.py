from __future__ import annotations

from pathlib import Path

from photo_processor.core.image_info import ImageInfo
from photo_processor.core.settings import ProcessingSettings
from photo_processor.infra.imaging.image_loader import load_image
from photo_processor.infra.imaging.pillow_transformer import render_to_frame
from photo_processor.infra.imaging.resize_planner import build_resize_plan


def build_manual_preview(source_path: Path, settings: ProcessingSettings) -> tuple[object, ImageInfo, tuple[int, int], ImageInfo]:
    loaded = load_image(source_path)
    image = loaded.image
    source_info = ImageInfo(
        width=image.width,
        height=image.height,
        mode=image.mode,
        image_format=loaded.image_format,
    )
    target_width, target_height, plan = build_resize_plan(
        settings,
        source_width=image.width,
        source_height=image.height,
    )
    transformed = render_to_frame(image, target_width, target_height, plan)
    target_info = ImageInfo(
        width=target_width,
        height=target_height,
        mode=transformed.mode,
        image_format=settings.output_policy.output_format.value.upper(),
    )
    return transformed, source_info, (target_width, target_height), target_info
