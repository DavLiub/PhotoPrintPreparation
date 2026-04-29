from __future__ import annotations

from dataclasses import dataclass

from photo_processor.core.settings import CropAnchor


@dataclass(slots=True)
class ResizePlan:
    resized_width: int
    resized_height: int
    crop_box: tuple[int, int, int, int] | None = None
    padding: tuple[int, int, int, int] | None = None


def _scale(source_width: int, source_height: int, factor: float) -> tuple[int, int]:
    return max(1, round(source_width * factor)), max(1, round(source_height * factor))


def calculate_contain_size(source_width: int, source_height: int, frame_width: int, frame_height: int) -> ResizePlan:
    factor = min(frame_width / source_width, frame_height / source_height)
    resized_width, resized_height = _scale(source_width, source_height, factor)
    padding = calculate_padding(resized_width, resized_height, frame_width, frame_height)
    return ResizePlan(resized_width, resized_height, padding=padding)


def calculate_fit_width_size(
    source_width: int,
    source_height: int,
    frame_width: int,
    frame_height: int,
    crop_anchor: CropAnchor = CropAnchor.TOP_LEFT,
) -> ResizePlan:
    factor = frame_width / source_width
    resized_width, resized_height = _scale(source_width, source_height, factor)
    crop_box = calculate_crop_box(resized_width, resized_height, frame_width, frame_height, crop_anchor)
    return ResizePlan(resized_width, resized_height, crop_box=crop_box)


def calculate_fit_height_size(
    source_width: int,
    source_height: int,
    frame_width: int,
    frame_height: int,
    crop_anchor: CropAnchor = CropAnchor.TOP_LEFT,
) -> ResizePlan:
    factor = frame_height / source_height
    resized_width, resized_height = _scale(source_width, source_height, factor)
    padding = calculate_padding(resized_width, resized_height, frame_width, frame_height)
    crop_box = (
        None
        if resized_width <= frame_width
        else calculate_crop_box(resized_width, resized_height, frame_width, frame_height, crop_anchor)
    )
    return ResizePlan(resized_width, resized_height, crop_box=crop_box, padding=padding)


def calculate_crop_box(
    resized_width: int,
    resized_height: int,
    frame_width: int,
    frame_height: int,
    crop_anchor: CropAnchor = CropAnchor.TOP_LEFT,
) -> tuple[int, int, int, int]:
    max_left = max(0, resized_width - frame_width)
    max_top = max(0, resized_height - frame_height)

    if crop_anchor == CropAnchor.CENTER:
        left = max_left // 2
        top = max_top // 2
    elif crop_anchor == CropAnchor.TOP:
        left = max_left // 2
        top = 0
    elif crop_anchor == CropAnchor.LEFT:
        left = 0
        top = max_top // 2
    else:
        left = 0
        top = 0

    right = left + min(frame_width, resized_width)
    bottom = top + min(frame_height, resized_height)
    return left, top, right, bottom


def calculate_padding(resized_width: int, resized_height: int, frame_width: int, frame_height: int) -> tuple[int, int, int, int]:
    horizontal = max(0, frame_width - resized_width)
    vertical = max(0, frame_height - resized_height)
    left = horizontal // 2
    right = horizontal - left
    top = vertical // 2
    bottom = vertical - top
    return left, top, right, bottom
