from __future__ import annotations

from photo_processor.api.settings_factory import build_snapshot_from_settings
from photo_processor.core.settings import ProcessingSettings
from photo_processor.core.settings_snapshot import SettingsSnapshot
from photo_processor.infra.settings_storage.json_settings_storage import JsonSettingsStorage


class SettingsController:
    def __init__(self, storage: JsonSettingsStorage) -> None:
        self.storage = storage

    def load_snapshot(self) -> SettingsSnapshot | None:
        return self.storage.load()

    def save_settings(self, settings: ProcessingSettings, preset_id: str | None) -> None:
        self.storage.save(build_snapshot_from_settings(settings, preset_id))
