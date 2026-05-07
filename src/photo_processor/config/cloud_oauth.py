from __future__ import annotations

import os

try:
    from photo_processor.config.cloud_oauth_embedded import GOOGLE_DRIVE_CLIENT_ID as EMBEDDED_GOOGLE_DRIVE_CLIENT_ID
    from photo_processor.config.cloud_oauth_embedded import GOOGLE_DRIVE_CLIENT_SECRET as EMBEDDED_GOOGLE_DRIVE_CLIENT_SECRET
except ImportError:
    EMBEDDED_GOOGLE_DRIVE_CLIENT_ID = None
    EMBEDDED_GOOGLE_DRIVE_CLIENT_SECRET = None


GOOGLE_DRIVE_CLIENT_ID_ENV = "PHOTO_PROCESSOR_GDRIVE_CLIENT_ID"
GOOGLE_DRIVE_CLIENT_SECRET_ENV = "PHOTO_PROCESSOR_GDRIVE_CLIENT_SECRET"


def get_google_drive_client_id() -> str:
    value = os.getenv(GOOGLE_DRIVE_CLIENT_ID_ENV, "").strip()
    if value:
        return value
    if EMBEDDED_GOOGLE_DRIVE_CLIENT_ID:
        return str(EMBEDDED_GOOGLE_DRIVE_CLIENT_ID).strip()
    raise RuntimeError(
        "Missing Google Drive app credential. "
        f"Set {GOOGLE_DRIVE_CLIENT_ID_ENV} or provide src/photo_processor/config/cloud_oauth_embedded.py for this application."
    )


def get_google_drive_client_secret() -> str | None:
    value = os.getenv(GOOGLE_DRIVE_CLIENT_SECRET_ENV, "").strip()
    if value:
        return value
    if EMBEDDED_GOOGLE_DRIVE_CLIENT_SECRET:
        return str(EMBEDDED_GOOGLE_DRIVE_CLIENT_SECRET).strip()
    return None
