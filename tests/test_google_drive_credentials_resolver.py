import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.core.cloud_upload import CloudProvider, CloudUploadSettings
from photo_processor.core.settings import ProcessingSettings
from photo_processor.infra.cloud.google_drive_credentials_resolver import GoogleDriveCredentialsResolver


class InMemorySecretStore:
    def __init__(self, initial: dict[str, str] | None = None) -> None:
        self.data = dict(initial or {})

    def load_secret(self, key: str) -> str | None:
        return self.data.get(key)

    def save_secret(self, key: str, value: str) -> None:
        self.data[key] = value

    def delete_secret(self, key: str) -> None:
        self.data.pop(key, None)


class GoogleDriveCredentialsResolverTestCase(unittest.TestCase):
    def test_resolve_prefers_saved_secret(self) -> None:
        settings = ProcessingSettings(
            source_folder=Path("src"),
            output_folder=Path("out"),
            cloud_upload=CloudUploadSettings(
                enabled=True,
                provider=CloudProvider.GOOGLE_DRIVE,
                connection_id="primary",
            ),
        )
        store = InMemorySecretStore(
            {
                "google_drive:primary": json.dumps(
                    {
                        "client_id": "saved-client",
                        "refresh_token": "saved-refresh",
                    }
                )
            }
        )

        credentials = GoogleDriveCredentialsResolver(secret_store=store).resolve(settings)

        self.assertEqual(credentials.client_id, "saved-client")
        self.assertEqual(credentials.refresh_token, "saved-refresh")
        self.assertIsNone(credentials.client_secret)

    def test_resolve_falls_back_to_environment_variables(self) -> None:
        settings = ProcessingSettings(
            source_folder=Path("src"),
            output_folder=Path("out"),
            cloud_upload=CloudUploadSettings(
                enabled=True,
                provider=CloudProvider.GOOGLE_DRIVE,
            ),
        )
        with patch.dict(
            os.environ,
            {
                "PHOTO_PROCESSOR_GDRIVE_CLIENT_ID": "env-client",
                "PHOTO_PROCESSOR_GDRIVE_REFRESH_TOKEN": "env-refresh",
                "PHOTO_PROCESSOR_GDRIVE_CLIENT_SECRET": "env-secret",
            },
            clear=False,
        ):
            credentials = GoogleDriveCredentialsResolver(secret_store=InMemorySecretStore()).resolve(settings)

        self.assertEqual(credentials.client_id, "env-client")
        self.assertEqual(credentials.refresh_token, "env-refresh")
        self.assertEqual(credentials.client_secret, "env-secret")
