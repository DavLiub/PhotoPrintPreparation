from __future__ import annotations

from photo_processor.infra.cloud.google_drive_credentials_resolver import GoogleDriveCredentialsResolver


class DisconnectGoogleDriveUseCase:
    def __init__(self, credentials_resolver: GoogleDriveCredentialsResolver) -> None:
        self.credentials_resolver = credentials_resolver

    def run(self, connection_id: str | None) -> None:
        if not connection_id:
            return
        self.credentials_resolver.delete(connection_id)
