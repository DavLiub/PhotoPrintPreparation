from __future__ import annotations

from pathlib import Path

from photo_processor.core.output_policy import ConflictStrategy, OutputPolicy


def build_output_path(source_path: Path, output_folder: Path, policy: OutputPolicy) -> Path | None:
    stem = f"{source_path.stem}{policy.filename_suffix}"
    extension = policy.output_format.extension
    candidate = output_folder / f"{stem}{extension}"

    if policy.conflict_strategy == ConflictStrategy.OVERWRITE:
        return candidate

    if policy.conflict_strategy == ConflictStrategy.SKIP and candidate.exists():
        return None

    counter = 1
    while candidate.exists():
        candidate = output_folder / f"{stem}_{counter}{extension}"
        counter += 1

    return candidate
