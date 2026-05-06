import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.app.use_cases.connect_google_drive import ConnectGoogleDriveUseCase
from photo_processor.app.use_cases.disconnect_google_drive import DisconnectGoogleDriveUseCase
from photo_processor.infra.cloud.google_drive_credentials_resolver import GoogleDriveCredentialsResolver
from photo_processor.infra.cloud.google_drive_oauth import GoogleDriveAuthorizationResult
from photo_processor.infra.cloud.google_drive_uploader import GoogleDriveCredentials


class InMemorySecretStore:
    def __init__(self) -> None:
        self.data: dict[str, str] = {}

    def load_secret(self, key: str) -> str | None:
        return self.data.get(key)

    def save_secret(self, key: str, value: str) -> None:
        self.data[key] = value

    def delete_secret(self, key: str) -> None:
        self.data.pop(key, None)


class FakeGoogleDriveOAuthFlow:
    def __init__(self, account_email: str = "user@example.com") -> None:
        self.account_email = account_email
        self.client_ids: list[str] = []
        self.client_secrets: list[str | None] = []

    def authorize(self, client_id: str, client_secret: str | None = None) -> GoogleDriveAuthorizationResult:
        self.client_ids.append(client_id)
        self.client_secrets.append(client_secret)
        return GoogleDriveAuthorizationResult(
            credentials=GoogleDriveCredentials(
                client_id=client_id,
                refresh_token="refresh-token",
                client_secret=client_secret,
            ),
            account_email=self.account_email,
        )


class GoogleDriveConnectUseCasesTestCase(unittest.TestCase):
    def test_connect_saves_credentials_and_returns_connection_info(self) -> None:
        store = InMemorySecretStore()
        resolver = GoogleDriveCredentialsResolver(secret_store=store)
        flow = FakeGoogleDriveOAuthFlow(account_email="photo.user@example.com")

        with patch(
            "photo_processor.app.use_cases.connect_google_drive.get_google_drive_client_id",
            return_value="client-123",
        ):
            result = ConnectGoogleDriveUseCase(flow, resolver).run()

        self.assertEqual(flow.client_ids, ["client-123"])
        self.assertEqual(flow.client_secrets, [None])
        self.assertEqual(result.account_email, "photo.user@example.com")
        self.assertEqual(result.connection_id, "google_drive_photo_user_example_com")
        self.assertIn(f"google_drive:{result.connection_id}", store.data)

    def test_disconnect_removes_saved_credentials(self) -> None:
        store = InMemorySecretStore()
        resolver = GoogleDriveCredentialsResolver(secret_store=store)
        resolver.save(
            "google_drive_user_example_com",
            GoogleDriveCredentials(client_id="client-123", refresh_token="refresh-token"),
        )

        DisconnectGoogleDriveUseCase(resolver).run("google_drive_user_example_com")

        self.assertEqual(store.data, {})
