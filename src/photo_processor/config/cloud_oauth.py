from __future__ import annotations

import os


GOOGLE_DRIVE_CLIENT_ID_ENV = "PHOTO_PROCESSOR_GDRIVE_CLIENT_ID"
GOOGLE_DRIVE_CLIENT_SECRET_ENV = "PHOTO_PROCESSOR_GDRIVE_CLIENT_SECRET"


def get_google_drive_client_id() -> str:
    value = os.getenv(GOOGLE_DRIVE_CLIENT_ID_ENV, "").strip()
    if value:
        return value
    raise RuntimeError(
        f"Missing Google Drive app credential. Set {GOOGLE_DRIVE_CLIENT_ID_ENV} for this application."
    )


def get_google_drive_client_secret() -> str | None:
    value = os.getenv(GOOGLE_DRIVE_CLIENT_SECRET_ENV, "").strip()
    return value or None
