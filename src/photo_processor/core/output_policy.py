from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OutputFormat(str, Enum):
    JPEG = "jpeg"

    @property
    def extension(self) -> str:
        if self is OutputFormat.JPEG:
            return ".jpg"
        raise ValueError(f"Unsupported output format: {self}")


class ConflictStrategy(str, Enum):
    ADD_COUNTER = "add_counter"
    OVERWRITE = "overwrite"
    SKIP = "skip"


@dataclass(slots=True)
class OutputPolicy:
    filename_suffix: str
    output_format: OutputFormat
    conflict_strategy: ConflictStrategy = ConflictStrategy.ADD_COUNTER

