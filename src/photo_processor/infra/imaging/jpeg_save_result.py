from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class JpegSaveResult:
    output_size: tuple[int, int]
    file_size_bytes: int
    quality: int
    was_dimension_reduced: bool

