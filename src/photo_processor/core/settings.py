from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from photo_processor.config.defaults import (
    DEFAULT_DPI,
    DEFAULT_FILENAME_SUFFIX,
    DEFAULT_HEIGHT,
    DEFAULT_MAX_FILE_SIZE_MB,
    DEFAULT_WIDTH,
)
from photo_processor.core.output_policy import OutputFormat, OutputPolicy


class Units(str, Enum):
    PIXELS = "pixels"
    CENTIMETERS = "centimeters"


class ResizeMode(str, Enum):
    CONTAIN = "contain"
    FIT_WIDTH = "fit_width"
    FIT_HEIGHT = "fit_height"


class CropAnchor(str, Enum):
    CENTER = "center"
    TOP_LEFT = "top_left"
    TOP = "top"
    LEFT = "left"


SUPPORTED_INPUT_FORMATS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


@dataclass(slots=True)
class ProcessingSettings:
    source_folder: Path
    output_folder: Path
    width: float = DEFAULT_WIDTH
    height: float = DEFAULT_HEIGHT
    units: Units = Units.PIXELS
    dpi: int = DEFAULT_DPI
    resize_mode: ResizeMode = ResizeMode.CONTAIN
    crop_anchor: CropAnchor = CropAnchor.TOP_LEFT
    allow_both_orientations: bool = True
    auto_rotate: bool = True
    max_file_size_mb: float = DEFAULT_MAX_FILE_SIZE_MB
    keep_aspect_ratio: bool = True
    source_formats: tuple[str, ...] = field(default_factory=lambda: SUPPORTED_INPUT_FORMATS)
    output_policy: OutputPolicy = field(
        default_factory=lambda: OutputPolicy(
            filename_suffix=DEFAULT_FILENAME_SUFFIX,
            output_format=OutputFormat.JPEG,
        )
    )

    def target_size_px(self) -> tuple[int, int]:
        if self.units == Units.PIXELS:
            return round(self.width), round(self.height)

        scale = self.dpi / 2.54
        return round(self.width * scale), round(self.height * scale)
