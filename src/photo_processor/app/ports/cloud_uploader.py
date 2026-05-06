from __future__ import annotations

from pathlib import Path
from typing import Protocol

from photo_processor.core.cloud_upload import CloudUploadSettings, UploadResult


class CloudUploader(Protocol):
    def upload(self, local_path: Path, settings: CloudUploadSettings) -> UploadResult:
        ...
