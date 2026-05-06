from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CloudProvider(str, Enum):
    GOOGLE_DRIVE = "google_drive"
    DROPBOX = "dropbox"


class UploadStatus(str, Enum):
    SUCCESS = "success"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass(slots=True, frozen=True)
class CloudUploadSettings:
    enabled: bool = False
    provider: CloudProvider | None = None
    connection_id: str | None = None
    account_email: str | None = None
    remote_folder: str | None = None
    remote_folder_display: str | None = None
    remote_folder_share_link: str | None = None
    create_share_link: bool = False
    delete_local_after_upload: bool = False
    overwrite_remote: bool = False

    @property
    def is_enabled(self) -> bool:
        return self.enabled and self.provider is not None


@dataclass(slots=True, frozen=True)
class UploadResult:
    provider: CloudProvider
    status: UploadStatus
    remote_path: str | None = None
    remote_url: str | None = None
    file_id: str | None = None
    error_message: str | None = None
