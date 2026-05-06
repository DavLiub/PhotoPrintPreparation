from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ProcessingReport:
    found_files: int
    processed_files: int
    skipped_files: int
    error_files: int
    uploaded_files: int
    upload_skipped_files: int
    upload_error_files: int
    uploaded_bytes: int
    warning_count: int
    cloud_provider: str | None = None
    cloud_remote_folder: str | None = None
    summary_lines: list[str] = field(default_factory=list)
