from __future__ import annotations

from photo_processor.core.preset import ProcessingPreset
from photo_processor.core.settings import ResizeMode, Units

PHOTO_REPORT = ProcessingPreset(
    preset_id="photo_report",
    display_name="Photo Report",
    width=1500,
    height=1000,
    units=Units.PIXELS,
    dpi=300,
    resize_mode=ResizeMode.CONTAIN,
    max_file_size_mb=2.0,
)

PRINT_10X15 = ProcessingPreset(
    preset_id="print_10x15",
    display_name="Print 10x15 cm",
    width=15,
    height=10,
    units=Units.CENTIMETERS,
    dpi=300,
    resize_mode=ResizeMode.CONTAIN,
    max_file_size_mb=5.0,
)

EMAIL_CLOUD = ProcessingPreset(
    preset_id="email_cloud",
    display_name="Email / Cloud",
    width=1600,
    height=1200,
    units=Units.PIXELS,
    dpi=300,
    resize_mode=ResizeMode.CONTAIN,
    max_file_size_mb=1.5,
)

PRESETS: dict[str, ProcessingPreset] = {
    PHOTO_REPORT.preset_id: PHOTO_REPORT,
    PRINT_10X15.preset_id: PRINT_10X15,
    EMAIL_CLOUD.preset_id: EMAIL_CLOUD,
}


def get_preset(preset_id: str) -> ProcessingPreset:
    return PRESETS[preset_id]


def get_preset_ids() -> list[str]:
    return sorted(PRESETS)
