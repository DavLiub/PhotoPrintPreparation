from __future__ import annotations

from photo_processor.core.image_info import ImageInfo
from photo_processor.core.image_task import ImageTask
from photo_processor.core.settings import ProcessingSettings
from photo_processor.core.single_image_result import ImageProcessStatus, SingleImageResult
from photo_processor.infra.imaging.image_loader import load_image
from photo_processor.infra.imaging.jpeg_optimizer import save_jpeg_with_limit
from photo_processor.infra.imaging.pillow_transformer import render_to_frame
from photo_processor.infra.imaging.resize_planner import build_resize_plan


class ImageProcessor:
    def __init__(self, settings: ProcessingSettings) -> None:
        self.settings = settings

    def process(self, task: ImageTask) -> SingleImageResult:
        loaded = load_image(task.source_path)
        image = loaded.image
        source_info = ImageInfo(
            width=image.width,
            height=image.height,
            mode=image.mode,
            image_format=loaded.image_format,
        )
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
        if source_info.width < target_width or source_info.height < target_height:
            warnings.append("Source image is smaller than the target frame; output quality may be reduced.")
        if save_result.was_dimension_reduced:
            warnings.append("Output dimensions were reduced to satisfy the file size limit.")

        return SingleImageResult(
            source_path=task.source_path,
            output_path=task.output_path,
            status=ImageProcessStatus.SUCCESS,
            warnings=warnings,
            source_info=source_info,
            target_size=(target_width, target_height),
            output_info=ImageInfo(
                width=save_result.output_size[0],
                height=save_result.output_size[1],
                mode="RGB",
                image_format=self.settings.output_policy.output_format.value.upper(),
            ),
            output_file_size_bytes=save_result.file_size_bytes,
            output_quality=save_result.quality,
            was_dimension_reduced=save_result.was_dimension_reduced,
        )
