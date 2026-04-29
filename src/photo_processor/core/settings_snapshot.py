from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SettingsSnapshot:
    preset_id: str | None = None
    source_folder: str | None = None
    output_folder: str | None = None
    width: float | None = None
    height: float | None = None
    units: str | None = None
    dpi: int | None = None
    resize_mode: str | None = None
    max_file_size_mb: float | None = None
    filename_suffix: str | None = None
    conflict_strategy: str | None = None
    source_formats: tuple[str, ...] | None = None
    output_format: str | None = None
