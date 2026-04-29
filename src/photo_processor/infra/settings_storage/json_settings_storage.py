from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from photo_processor.core.settings_snapshot import SettingsSnapshot


class JsonSettingsStorage:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> SettingsSnapshot | None:
        if not self.path.exists():
            return None

        data = json.loads(self.path.read_text(encoding="utf-8"))
        return SettingsSnapshot(**data)

    def save(self, snapshot: SettingsSnapshot) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(asdict(snapshot), indent=2),
            encoding="utf-8",
        )
