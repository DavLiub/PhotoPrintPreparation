from __future__ import annotations

from photo_processor.core.processing_report import ProcessingReport
from photo_processor.core.processing_result import BatchProcessingResult
from photo_processor.core.settings import ProcessingSettings


def build_processing_report(
    result: BatchProcessingResult,
    settings: ProcessingSettings | None = None,
) -> ProcessingReport:
    warning_count = sum(len(item.warnings) for item in result.items)
    uploaded_bytes = sum(
        item.output_file_size_bytes or 0
        for item in result.items
        if item.upload_result is not None and item.upload_result.status.value == "success"
    )
    cloud_provider = None
    cloud_remote_folder = None
    if settings is not None and settings.cloud_upload.provider is not None:
        cloud_provider = settings.cloud_upload.provider.value
        cloud_remote_folder = settings.cloud_upload.remote_folder_display or settings.cloud_upload.remote_folder
    summary_lines = [
        f"Found files: {result.found_files}",
        f"Processed: {result.processed_files}",
        f"Skipped: {result.skipped_files}",
        f"Errors: {result.error_files}",
        f"Uploaded: {result.uploaded_files}",
        f"Upload skipped: {result.upload_skipped_files}",
        f"Upload errors: {result.upload_error_files}",
        f"Uploaded size: {round(uploaded_bytes / (1024 * 1024), 2)} MB",
        f"Warnings: {warning_count}",
    ]
    if cloud_provider:
        summary_lines.append(f"Cloud provider: {cloud_provider}")
    if cloud_remote_folder:
        summary_lines.append(f"Cloud folder: {cloud_remote_folder}")
    return ProcessingReport(
        found_files=result.found_files,
        processed_files=result.processed_files,
        skipped_files=result.skipped_files,
        error_files=result.error_files,
        uploaded_files=result.uploaded_files,
        upload_skipped_files=result.upload_skipped_files,
        upload_error_files=result.upload_error_files,
        uploaded_bytes=uploaded_bytes,
        cloud_provider=cloud_provider,
        cloud_remote_folder=cloud_remote_folder,
        warning_count=warning_count,
        summary_lines=summary_lines,
    )
