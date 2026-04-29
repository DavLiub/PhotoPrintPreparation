from __future__ import annotations


def rotated_size(width: int, height: int) -> tuple[int, int]:
    return height, width


def orientation_score(image_width: int, image_height: int, frame_width: int, frame_height: int) -> float:
    image_ratio = image_width / image_height
    frame_ratio = frame_width / frame_height
    return abs(image_ratio - frame_ratio)


def should_rotate_for_better_fit(image_width: int, image_height: int, frame_width: int, frame_height: int) -> bool:
    normal_score = orientation_score(image_width, image_height, frame_width, frame_height)
    rotated_score = orientation_score(image_height, image_width, frame_width, frame_height)
    return rotated_score < normal_score


def choose_target_frame(
    frame_width: int,
    frame_height: int,
    image_width: int,
    image_height: int,
    allow_both_orientations: bool,
    auto_rotate: bool,
) -> tuple[int, int]:
    if not allow_both_orientations:
        return frame_width, frame_height

    if auto_rotate and should_rotate_for_better_fit(image_width, image_height, frame_width, frame_height):
        return frame_height, frame_width

    return frame_width, frame_height
