from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class BatchProcessingResult:
    found_files: int = 0
    processed_files: int = 0
    skipped_files: int = 0
    error_files: int = 0
    messages: list[str] = field(default_factory=list)
