from __future__ import annotations

from photo_processor.core.image_task import ImageTask
from photo_processor.core.settings import ProcessingSettings
from photo_processor.core.single_image_result import SingleImageResult
from photo_processor.infra.imaging.image_loader import load_image
from photo_processor.infra.imaging.jpeg_optimizer import save_jpeg_with_limit
from photo_processor.infra.imaging.pillow_transformer import render_to_frame
from photo_processor.infra.imaging.resize_planner import build_resize_plan


class ImageProcessor:
    def __init__(self, settings: ProcessingSettings) -> None:
        self.settings = settings

    def process(self, task: ImageTask) -> SingleImageResult:
        image = load_image(task.source_path)
        source_size = (image.width, image.height)
        target_width, target_height, plan = build_resize_plan(
            self.settings,
            source_width=image.width,
            source_height=image.height,
        )
        transformed = render_to_frame(image, target_width, target_height, plan)
        save_result = save_jpeg_with_limit(
            transformed,
            output_path=task.output_path,
            max_file_size_mb=self.settings.max_file_size_mb,
        )
        warnings: list[str] = []
        if save_result.was_dimension_reduced:
            warnings.append("Output dimensions were reduced to satisfy the file size limit.")

        return SingleImageResult(
            source_path=task.source_path,
            output_path=task.output_path,
            success=True,
            warnings=warnings,
            source_size=source_size,
            target_size=(target_width, target_height),
            output_size=save_result.output_size,
            output_file_size_bytes=save_result.file_size_bytes,
            output_quality=save_result.quality,
            was_dimension_reduced=save_result.was_dimension_reduced,
        )
