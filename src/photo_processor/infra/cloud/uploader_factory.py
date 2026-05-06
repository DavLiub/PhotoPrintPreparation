from __future__ import annotations

from photo_processor.app.ports.cloud_uploader import CloudUploader
from photo_processor.core.cloud_upload import CloudProvider
from photo_processor.core.settings import ProcessingSettings
from photo_processor.infra.cloud.google_drive_credentials_resolver import GoogleDriveCredentialsResolver
from photo_processor.infra.cloud.google_drive_uploader import GoogleDriveUploader
from photo_processor.infra.secrets.windows_dpapi_store import WindowsDPAPISecretStore
from photo_processor.infra.settings_storage.storage_paths import resolve_secret_store_dir


def build_cloud_uploader(settings: ProcessingSettings) -> CloudUploader:
    provider = settings.cloud_upload.provider
    if provider is CloudProvider.GOOGLE_DRIVE:
        secret_store = WindowsDPAPISecretStore(resolve_secret_store_dir())
        credentials = GoogleDriveCredentialsResolver(secret_store=secret_store).resolve(settings)
        return GoogleDriveUploader(credentials)
    if provider is CloudProvider.DROPBOX:
        raise NotImplementedError("Dropbox upload is planned but not implemented yet.")
    raise RuntimeError("Cloud upload is enabled but no supported provider is configured.")
