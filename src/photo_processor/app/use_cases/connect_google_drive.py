from __future__ import annotations

from dataclasses import dataclass

from photo_processor.config.cloud_oauth import get_google_drive_client_id, get_google_drive_client_secret
from photo_processor.infra.cloud.google_drive_credentials_resolver import GoogleDriveCredentialsResolver
from photo_processor.infra.cloud.google_drive_oauth import GoogleDriveOAuthFlow


@dataclass(frozen=True, slots=True)
class GoogleDriveConnection:
    connection_id: str
    account_email: str


class ConnectGoogleDriveUseCase:
    def __init__(
        self,
        oauth_flow: GoogleDriveOAuthFlow,
        credentials_resolver: GoogleDriveCredentialsResolver,
    ) -> None:
        self.oauth_flow = oauth_flow
        self.credentials_resolver = credentials_resolver

    def run(self) -> GoogleDriveConnection:
        client_id = get_google_drive_client_id()
        client_secret = get_google_drive_client_secret()
        auth_result = self.oauth_flow.authorize(client_id=client_id, client_secret=client_secret)
        connection_id = _build_connection_id(auth_result.account_email)
        self.credentials_resolver.save(connection_id, auth_result.credentials)
        return GoogleDriveConnection(
            connection_id=connection_id,
            account_email=auth_result.account_email,
        )


def _build_connection_id(account_email: str) -> str:
    normalized = account_email.strip().lower()
    safe = "".join(ch if ch.isalnum() else "_" for ch in normalized)
    return f"google_drive_{safe}"
