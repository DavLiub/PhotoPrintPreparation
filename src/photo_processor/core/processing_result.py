from __future__ import annotations

from dataclasses import dataclass, field

from photo_processor.core.cloud_upload import UploadResult, UploadStatus
from photo_processor.core.single_image_result import ImageProcessStatus, SingleImageResult


@dataclass(slots=True)
class BatchProcessingResult:
    found_files: int = 0
    processed_files: int = 0
    skipped_files: int = 0
    error_files: int = 0
    uploaded_files: int = 0
    upload_skipped_files: int = 0
    upload_error_files: int = 0
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

    def add_upload_result(self, item: SingleImageResult, upload_result: UploadResult) -> None:
        item.upload_result = upload_result
        if upload_result.status is UploadStatus.SUCCESS:
            self.uploaded_files += 1
            target = upload_result.remote_url or upload_result.remote_path or upload_result.file_id or upload_result.provider.value
            self.messages.append(f"UPLOAD OK {item.output_path} -> {target}")
            return
        if upload_result.status is UploadStatus.SKIPPED:
            self.upload_skipped_files += 1
            detail = upload_result.error_message or "upload skipped"
            self.messages.append(f"UPLOAD SKIP {item.output_path}: {detail}")
            return

        self.upload_error_files += 1
        detail = upload_result.error_message or "upload failed"
        self.messages.append(f"UPLOAD ERROR {item.output_path}: {detail}")

    @property
    def warning_count(self) -> int:
        return sum(len(item.warnings) for item in self.items)
