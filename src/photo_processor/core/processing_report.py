from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ProcessingReport:
    found_files: int
    processed_files: int
    skipped_files: int
    error_files: int
    warning_count: int
    summary_lines: list[str] = field(default_factory=list)

