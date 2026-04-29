from __future__ import annotations

from dataclasses import dataclass, field

from photo_processor.core.single_image_result import ImageProcessStatus, SingleImageResult


@dataclass(slots=True)
class BatchProcessingResult:
    found_files: int = 0
    processed_files: int = 0
    skipped_files: int = 0
    error_files: int = 0
    items: list[SingleImageResult] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)

    def add_item(self, item: SingleImageResult) -> None:
        self.items.append(item)
        self.messages.append(item.summary_message())
        if item.status is ImageProcessStatus.SUCCESS:
            self.processed_files += 1
        elif item.status is ImageProcessStatus.SKIPPED:
            self.skipped_files += 1
        else:
            self.error_files += 1
