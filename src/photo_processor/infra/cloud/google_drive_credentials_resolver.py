from __future__ import annotations

import json
import os
from dataclasses import asdict

from photo_processor.config.cloud_oauth import get_google_drive_client_id, get_google_drive_client_secret
from photo_processor.core.settings import ProcessingSettings
from photo_processor.infra.cloud.google_drive_uploader import GoogleDriveCredentials
from photo_processor.infra.secrets.secret_store import SecretStore


class GoogleDriveCredentialsResolver:
    def __init__(self, secret_store: SecretStore | None = None) -> None:
        self.secret_store = secret_store

    def resolve(self, settings: ProcessingSettings) -> GoogleDriveCredentials:
        connection_id = settings.cloud_upload.connection_id
        if connection_id and self.secret_store is not None:
            secret = self.secret_store.load_secret(self._secret_key(connection_id))
            if secret:
                data = json.loads(secret)
                return GoogleDriveCredentials(
                    client_id=data["client_id"],
                    refresh_token=data["refresh_token"],
                    client_secret=data.get("client_secret"),
                )

        client_id = get_google_drive_client_id()
        refresh_token = _required_env("PHOTO_PROCESSOR_GDRIVE_REFRESH_TOKEN")
        client_secret = os.getenv("PHOTO_PROCESSOR_GDRIVE_CLIENT_SECRET") or get_google_drive_client_secret()
        return GoogleDriveCredentials(
            client_id=client_id,
            refresh_token=refresh_token,
            client_secret=client_secret,
        )

    def save(self, connection_id: str, credentials: GoogleDriveCredentials) -> None:
        if self.secret_store is None:
            raise RuntimeError("No secret store is configured for Google Drive credentials.")
        self.secret_store.save_secret(self._secret_key(connection_id), json.dumps(asdict(credentials)))

    def delete(self, connection_id: str) -> None:
        if self.secret_store is None:
            return
        self.secret_store.delete_secret(self._secret_key(connection_id))

    def _secret_key(self, connection_id: str) -> str:
        return f"google_drive:{connection_id}"


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(
        f"Missing Google Drive credentials. Expected a saved browser-based OAuth connection or environment variable {name}."
    )
