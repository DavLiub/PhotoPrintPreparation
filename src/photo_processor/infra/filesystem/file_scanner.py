from __future__ import annotations

from pathlib import Path


def scan_supported_images(source_folder: Path, extensions: tuple[str, ...]) -> list[Path]:
    if not source_folder.exists():
        return []

    allowed = {extension.lower() for extension in extensions}
    return sorted(
        path
        for path in source_folder.iterdir()
        if path.is_file() and path.suffix.lower() in allowed
    )

