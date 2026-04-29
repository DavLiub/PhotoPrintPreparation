from __future__ import annotations

from photo_processor.core.image_task import ImageTask
from photo_processor.core.settings import ProcessingSettings
from photo_processor.infra.imaging.image_loader import load_image
from photo_processor.infra.imaging.jpeg_optimizer import save_jpeg_with_limit
from photo_processor.infra.imaging.pillow_transformer import render_to_frame
from photo_processor.infra.imaging.resize_planner import build_resize_plan


class ImageProcessor:
    def __init__(self, settings: ProcessingSettings) -> None:
        self.settings = settings

    def process(self, task: ImageTask) -> None:
        image = load_image(task.source_path)
        target_width, target_height, plan = build_resize_plan(
            self.settings,
            source_width=image.width,
            source_height=image.height,
        )
        transformed = render_to_frame(image, target_width, target_height, plan)
        save_jpeg_with_limit(
            transformed,
            output_path=task.output_path,
            max_file_size_mb=self.settings.max_file_size_mb,
        )
