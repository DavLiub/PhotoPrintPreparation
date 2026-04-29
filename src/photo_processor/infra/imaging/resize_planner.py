from __future__ import annotations

from photo_processor.core.orientation import choose_target_frame
from photo_processor.core.resize_rules import (
    ResizePlan,
    calculate_contain_size,
    calculate_fit_height_size,
    calculate_fit_width_size,
)
from photo_processor.core.settings import ProcessingSettings, ResizeMode


def build_resize_plan(
    settings: ProcessingSettings,
    source_width: int,
    source_height: int,
) -> tuple[int, int, ResizePlan]:
    frame_width, frame_height = settings.target_size_px()
    target_width, target_height = choose_target_frame(
        frame_width=frame_width,
        frame_height=frame_height,
        image_width=source_width,
        image_height=source_height,
        allow_both_orientations=settings.allow_both_orientations,
        auto_rotate=settings.auto_rotate,
    )

    if settings.resize_mode == ResizeMode.CONTAIN:
        plan = calculate_contain_size(source_width, source_height, target_width, target_height)
    elif settings.resize_mode == ResizeMode.FIT_WIDTH:
        plan = calculate_fit_width_size(source_width, source_height, target_width, target_height)
    else:
        plan = calculate_fit_height_size(source_width, source_height, target_width, target_height)

    return target_width, target_height, plan
