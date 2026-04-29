from __future__ import annotations

from photo_processor.core.image_task import ImageTask
from photo_processor.core.settings import ProcessingSettings


class ImageProcessor:
    def __init__(self, settings: ProcessingSettings) -> None:
        self.settings = settings

    def process(self, task: ImageTask) -> None:
        raise NotImplementedError(
            "Pixel-level image processing is not implemented yet. "
            "Add a Pillow-backed implementation in photo_processor.infra.imaging.image_processor."
        )
