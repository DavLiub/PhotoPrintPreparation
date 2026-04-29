from __future__ import annotations

from pathlib import Path


def build_output_path(source_path: Path, output_folder: Path, suffix: str, extension: str) -> Path:
    stem = f"{source_path.stem}{suffix}"
    candidate = output_folder / f"{stem}{extension}"
    counter = 1

    while candidate.exists():
        candidate = output_folder / f"{stem}_{counter}{extension}"
        counter += 1

    return candidate

