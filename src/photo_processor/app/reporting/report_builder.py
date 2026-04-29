from __future__ import annotations

from photo_processor.core.processing_report import ProcessingReport
from photo_processor.core.processing_result import BatchProcessingResult


def build_processing_report(result: BatchProcessingResult) -> ProcessingReport:
    warning_count = sum(len(item.warnings) for item in result.items)
    summary_lines = [
        f"Found files: {result.found_files}",
        f"Processed: {result.processed_files}",
        f"Skipped: {result.skipped_files}",
        f"Errors: {result.error_files}",
        f"Warnings: {warning_count}",
    ]
    return ProcessingReport(
        found_files=result.found_files,
        processed_files=result.processed_files,
        skipped_files=result.skipped_files,
        error_files=result.error_files,
        warning_count=warning_count,
        summary_lines=summary_lines,
    )
