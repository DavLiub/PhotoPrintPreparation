from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SettingsSnapshot:
    preset_id: str | None = None
    source_folder: str | None = None
    output_folder: str | None = None
    width: float | None = None
    height: float | None = None
    units: str | None = None
    dpi: int | None = None
    auto_rotate: bool | None = None
    resize_mode: str | None = None
    crop_anchor: str | None = None
    max_file_size_mb: float | None = None
    filename_suffix: str | None = None
    conflict_strategy: str | None = None
    source_formats: tuple[str, ...] | None = None
    output_format: str | None = None
    cloud_upload_enabled: bool | None = None
    cloud_provider: str | None = None
    cloud_connection_id: str | None = None
    cloud_account_email: str | None = None
    cloud_remote_folder: str | None = None
    cloud_create_share_link: bool | None = None
    cloud_delete_local_after_upload: bool | None = None
    cloud_overwrite_remote: bool | None = None
