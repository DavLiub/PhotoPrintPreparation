from __future__ import annotations

from pathlib import Path

from photo_processor.bootstrap.env_loader import load_cloud_oauth_env
from photo_processor.config.cloud_oauth import (
    GOOGLE_DRIVE_CLIENT_ID_ENV,
    GOOGLE_DRIVE_CLIENT_SECRET_ENV,
    get_google_drive_client_id,
    get_google_drive_client_secret,
)


def build_embedded_oauth_module() -> Path:
    load_cloud_oauth_env()
    client_id = get_google_drive_client_id()
    client_secret = get_google_drive_client_secret()
    if not client_secret:
        raise RuntimeError(
            "Missing Google Drive app credential. "
            f"Set {GOOGLE_DRIVE_CLIENT_SECRET_ENV} or place it in config/cloud_oauth.env before building."
        )

    target = Path(__file__).resolve().parents[1] / "config" / "cloud_oauth_embedded.py"
    target.write_text(
        (
            '"""Local generated file for release builds. Do not commit."""\n\n'
            f'GOOGLE_DRIVE_CLIENT_ID = {client_id!r}\n'
            f'GOOGLE_DRIVE_CLIENT_SECRET = {client_secret!r}\n'
        ),
        encoding="utf-8",
    )
    return target


def main() -> int:
    target = build_embedded_oauth_module()
    print(f"Embedded OAuth config written to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
