from __future__ import annotations


def centimeters_to_pixels(value_cm: float, dpi: int) -> int:
    return round((value_cm / 2.54) * dpi)


def pixels_to_centimeters(value_px: int, dpi: int) -> float:
    return (value_px / dpi) * 2.54
