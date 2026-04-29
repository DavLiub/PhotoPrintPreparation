from __future__ import annotations

from dataclasses import dataclass

from photo_processor.core.settings import ResizeMode, Units


@dataclass(frozen=True, slots=True)
class ProcessingPreset:
    preset_id: str
    display_name: str
    width: float
    height: float
    units: Units
    dpi: int
    resize_mode: ResizeMode
    max_file_size_mb: float
    allow_both_orientations: bool = True
    auto_rotate: bool = True
