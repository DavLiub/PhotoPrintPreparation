from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from photo_processor.core.image_info import ImageInfo


class ImageProcessStatus(str, Enum):
    SUCCESS = "success"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass(slots=True)
class SingleImageResult:
    source_path: Path
    output_path: Path
    status: ImageProcessStatus
    warnings: list[str] = field(default_factory=list)
    error_message: str | None = None
    source_info: ImageInfo | None = None
    target_size: tuple[int, int] | None = None
    output_info: ImageInfo | None = None
    output_file_size_bytes: int | None = None
    output_quality: int | None = None
    was_dimension_reduced: bool = False

    @property
    def success(self) -> bool:
        return self.status is ImageProcessStatus.SUCCESS

    def summary_message(self) -> str:
        if self.status is ImageProcessStatus.ERROR and self.error_message:
            return f"ERROR {self.source_path}: {self.error_message}"
        if self.status is ImageProcessStatus.SKIPPED:
            return f"SKIP {self.source_path} -> {self.output_path}"

        details: list[str] = []
        if self.output_info is not None:
            details.append(f"{self.output_info.width}x{self.output_info.height}")
        if self.output_file_size_bytes is not None:
            details.append(f"{self.output_file_size_bytes} bytes")
        if self.output_quality is not None:
            details.append(f"quality={self.output_quality}")
        if self.was_dimension_reduced:
            details.append("reduced-dimensions")

        suffix = f" ({', '.join(details)})" if details else ""
        return f"OK {self.source_path} -> {self.output_path}{suffix}"
