from __future__ import annotations

from photo_processor.core.preset import ProcessingPreset
from photo_processor.core.settings import ResizeMode, Units

PHOTO_REPORT = ProcessingPreset(
    preset_id="photo_report",
    display_name="1500x1000 px, 300 DPI, max 2.0 MB",
    width=1500,
    height=1000,
    units=Units.PIXELS,
    dpi=300,
    resize_mode=ResizeMode.CONTAIN,
    max_file_size_mb=2.0,
)

PRINT_10X15 = ProcessingPreset(
    preset_id="print_10x15",
    display_name="10x15 cm, 300 DPI, max 5.0 MB",
    width=15,
    height=10,
    units=Units.CENTIMETERS,
    dpi=300,
    resize_mode=ResizeMode.CONTAIN,
    max_file_size_mb=5.0,
)

PRINT_9X13 = ProcessingPreset(
    preset_id="print_9x13",
    display_name="9x13 cm, 300 DPI, max 4.0 MB",
    width=13,
    height=9,
    units=Units.CENTIMETERS,
    dpi=300,
    resize_mode=ResizeMode.CONTAIN,
    max_file_size_mb=4.0,
)

PRINT_13X18 = ProcessingPreset(
    preset_id="print_13x18",
    display_name="13x18 cm, 300 DPI, max 6.0 MB",
    width=18,
    height=13,
    units=Units.CENTIMETERS,
    dpi=300,
    resize_mode=ResizeMode.CONTAIN,
    max_file_size_mb=6.0,
)

EMAIL_CLOUD = ProcessingPreset(
    preset_id="email_cloud",
    display_name="1600x1200 px, 300 DPI, max 1.5 MB",
    width=1600,
    height=1200,
    units=Units.PIXELS,
    dpi=300,
    resize_mode=ResizeMode.CONTAIN,
    max_file_size_mb=1.5,
)

PRESETS: dict[str, ProcessingPreset] = {
    PHOTO_REPORT.preset_id: PHOTO_REPORT,
    PRINT_9X13.preset_id: PRINT_9X13,
    PRINT_10X15.preset_id: PRINT_10X15,
    PRINT_13X18.preset_id: PRINT_13X18,
    EMAIL_CLOUD.preset_id: EMAIL_CLOUD,
}


def get_preset(preset_id: str) -> ProcessingPreset:
    return PRESETS[preset_id]


def get_preset_ids() -> list[str]:
    return sorted(PRESETS)
