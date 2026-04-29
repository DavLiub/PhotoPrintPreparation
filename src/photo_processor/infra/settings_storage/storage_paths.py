from __future__ import annotations

import os
from pathlib import Path


def resolve_settings_path() -> Path:
    program_data = os.getenv("ProgramData")
    if program_data:
        return Path(program_data) / "PhotoPrintPreparation" / "settings.json"

    return Path.home() / ".photo_print_preparation" / "settings.json"
