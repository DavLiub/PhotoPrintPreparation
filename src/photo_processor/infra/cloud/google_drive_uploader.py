from __future__ import annotations

import json
import mimetypes
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from urllib import parse, request
from urllib.error import HTTPError, URLError

from photo_processor.core.cloud_upload import CloudProvider, CloudUploadSettings, UploadResult, UploadStatus


@dataclass(slots=True, frozen=True)
class GoogleDriveCredentials:
    client_id: str
    refresh_token: str
    client_secret: str | None = None


@dataclass(slots=True, frozen=True)
class GoogleDriveFolder:
    folder_id: str
    name: str
    parent_id: str | None = None


class GoogleDriveUploader:
    def __init__(
        self,
        credentials: GoogleDriveCredentials,
        requester: callable | None = None,
    ) -> None:
        self.credentials = credentials
        self.requester = requester or self._default_requester
        self._access_token: str | None = None
        self._access_token_expires_at = 0.0
        self._folder_cache: dict[str, GoogleDriveFolder] = {
            "root": GoogleDriveFolder(folder_id="root", name="My Drive", parent_id=None)
        }
        self._children_cache: dict[str, list[GoogleDriveFolder]] = {}

    def upload(self, local_path: Path, settings: CloudUploadSettings) -> UploadResult:
        access_token = self._refresh_access_token()
        existing_file_id = self._find_existing_file_id(
            access_token=access_token,
            filename=local_path.name,
            folder_id=settings.remote_folder,
        )
        remote_path = self._remote_path(settings.remote_folder, local_path.name)

        if existing_file_id and not settings.overwrite_remote:
            return UploadResult(
                provider=CloudProvider.GOOGLE_DRIVE,
                status=UploadStatus.SKIPPED,
                remote_path=remote_path,
                file_id=existing_file_id,
                error_message="Remote file already exists and overwrite is disabled.",
            )

        if existing_file_id:
            file_info = self._update_file(
                access_token=access_token,
                file_id=existing_file_id,
                local_path=local_path,
            )
        else:
            file_info = self._create_file(
                access_token=access_token,
                local_path=local_path,
                folder_id=settings.remote_folder,
            )

        file_id = file_info["id"]
        remote_url = None
        if settings.create_share_link:
            remote_url = self._create_public_link(access_token, file_id)

        return UploadResult(
            provider=CloudProvider.GOOGLE_DRIVE,
            status=UploadStatus.SUCCESS,
            remote_path=remote_path,
            remote_url=remote_url,
            file_id=file_id,
        )

    def list_folders(self, parent_id: str | None = None) -> list[GoogleDriveFolder]:
        cache_key = "root" if parent_id in (None, "", "root") else str(parent_id)
        cached = self._children_cache.get(cache_key)
        if cached is not None:
            return list(cached)
        access_token = self._refresh_access_token()
        target_parent_id = None if parent_id in (None, "", "root") else parent_id
        clauses = ["mimeType = 'application/vnd.google-apps.folder'", "trashed = false"]
        clauses.append(f"'{target_parent_id or 'root'}' in parents")
        query = " and ".join(clauses)
        url = (
            "https://www.googleapis.com/drive/v3/files?"
            + parse.urlencode(
                {
                    "q": query,
                    "fields": "files(id,name,parents)",
                    "pageSize": "200",
                    "orderBy": "name_natural",
                    "includeItemsFromAllDrives": "true",
                    "supportsAllDrives": "true",
                }
            )
        )
        data = self._request_json(
            method="GET",
            url=url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        folders: list[GoogleDriveFolder] = []
        for item in data.get("files", []):
            parents = item.get("parents") or []
            parent = str(parents[0]) if parents else None
            folder = GoogleDriveFolder(
                folder_id=str(item["id"]),
                name=str(item.get("name") or item["id"]),
                parent_id=parent,
            )
            folders.append(folder)
            self._folder_cache[folder.folder_id] = folder
        self._children_cache[cache_key] = list(folders)
        return list(folders)

    def get_folder(self, folder_id: str | None) -> GoogleDriveFolder:
        normalized_id = "root" if folder_id in (None, "", "root") else str(folder_id)
        cached = self._folder_cache.get(normalized_id)
        if cached is not None:
            return cached
        access_token = self._refresh_access_token()
        data = self._request_json(
            method="GET",
            url=(
                f"https://www.googleapis.com/drive/v3/files/{normalized_id}?"
                + parse.urlencode(
                    {
                        "fields": "id,name,parents",
                        "supportsAllDrives": "true",
                    }
                )
            ),
            headers={"Authorization": f"Bearer {access_token}"},
        )
        parents = data.get("parents") or []
        folder = GoogleDriveFolder(
            folder_id=str(data["id"]),
            name=str(data.get("name") or data["id"]),
            parent_id=str(parents[0]) if parents else None,
        )
        self._folder_cache[folder.folder_id] = folder
        return folder

    def get_folder_path(self, folder_id: str | None) -> str:
        return " / ".join(folder.name for folder in self.get_folder_chain(folder_id))

    def get_folder_chain(self, folder_id: str | None) -> list[GoogleDriveFolder]:
        folder = self.get_folder(folder_id)
        chain = [folder]
        parent_id = folder.parent_id
        while parent_id is not None:
            parent = self.get_folder(parent_id)
            chain.append(parent)
            parent_id = parent.parent_id
        chain.reverse()
        return chain

    def create_folder(self, name: str, parent_id: str | None = None) -> GoogleDriveFolder:
        folder_name = name.strip()
        if not folder_name:
            raise RuntimeError("Google Drive folder name cannot be empty.")
        access_token = self._refresh_access_token()
        metadata: dict[str, object] = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id not in (None, "", "root"):
            metadata["parents"] = [parent_id]
        data = self._request_json(
            method="POST",
            url="https://www.googleapis.com/drive/v3/files?supportsAllDrives=true&fields=id,name,parents",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            body=json.dumps(metadata).encode("utf-8"),
        )
        parents = data.get("parents") or []
        folder = GoogleDriveFolder(
            folder_id=str(data["id"]),
            name=str(data.get("name") or folder_name),
            parent_id=str(parents[0]) if parents else ("root" if parent_id in (None, "", "root") else parent_id),
        )
        self._folder_cache[folder.folder_id] = folder
        parent_cache_key = "root" if parent_id in (None, "", "root") else str(parent_id)
        self._children_cache.pop(parent_cache_key, None)
        return folder

    def get_or_create_folder_share_link(self, folder_id: str | None) -> str | None:
        if folder_id in (None, "", "root"):
            return None
        access_token = self._refresh_access_token()
        if not self._folder_has_public_link(access_token, folder_id):
            self._request_json(
                method="POST",
                url=f"https://www.googleapis.com/drive/v3/files/{folder_id}/permissions?supportsAllDrives=true",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                body=json.dumps(
                    {
                        "role": "reader",
                        "type": "anyone",
                        "allowFileDiscovery": False,
                    }
                ).encode("utf-8"),
            )
        return f"https://drive.google.com/drive/folders/{folder_id}?usp=sharing"

    def _refresh_access_token(self) -> str:
        if self._access_token and time.monotonic() < self._access_token_expires_at:
            return self._access_token
        payload_data = {
            "client_id": self.credentials.client_id,
            "refresh_token": self.credentials.refresh_token,
            "grant_type": "refresh_token",
        }
        if self.credentials.client_secret:
            payload_data["client_secret"] = self.credentials.client_secret
        payload = parse.urlencode(payload_data).encode("utf-8")
        data = self._request_json(
            method="POST",
            url="https://oauth2.googleapis.com/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body=payload,
        )
        token = data.get("access_token")
        if not token:
            raise RuntimeError("Google Drive token refresh did not return an access token.")
        expires_in = int(data.get("expires_in", 3600))
        self._access_token = str(token)
        self._access_token_expires_at = time.monotonic() + max(expires_in - 60, 60)
        return self._access_token

    def _find_existing_file_id(self, access_token: str, filename: str, folder_id: str | None) -> str | None:
        escaped_name = filename.replace("\\", "\\\\").replace("'", "\\'")
        clauses = [f"name = '{escaped_name}'", "trashed = false"]
        if folder_id:
            clauses.append(f"'{folder_id}' in parents")
        query = " and ".join(clauses)
        url = (
            "https://www.googleapis.com/drive/v3/files?"
            + parse.urlencode(
                {
                    "q": query,
                    "fields": "files(id,name)",
                    "pageSize": "1",
                    "includeItemsFromAllDrives": "true",
                    "supportsAllDrives": "true",
                }
            )
        )
        data = self._request_json(
            method="GET",
            url=url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        files = data.get("files", [])
        if not files:
            return None
        return str(files[0]["id"])

    def _create_file(self, access_token: str, local_path: Path, folder_id: str | None) -> dict[str, object]:
        metadata: dict[str, object] = {"name": local_path.name}
        if folder_id:
            metadata["parents"] = [folder_id]
        body, content_type = self._build_multipart_body(local_path, metadata)
        return self._request_json(
            method="POST",
            url=(
                "https://www.googleapis.com/upload/drive/v3/files"
                "?uploadType=multipart&supportsAllDrives=true&fields=id,name"
            ),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": content_type,
            },
            body=body,
        )

    def _update_file(self, access_token: str, file_id: str, local_path: Path) -> dict[str, object]:
        metadata = {"name": local_path.name}
        body, content_type = self._build_multipart_body(local_path, metadata)
        return self._request_json(
            method="PATCH",
            url=(
                f"https://www.googleapis.com/upload/drive/v3/files/{file_id}"
                "?uploadType=multipart&supportsAllDrives=true&fields=id,name"
            ),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": content_type,
            },
            body=body,
        )

    def _create_public_link(self, access_token: str, file_id: str) -> str:
        self._request_json(
            method="POST",
            url=f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions?supportsAllDrives=true",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            body=json.dumps({"role": "reader", "type": "anyone"}).encode("utf-8"),
        )
        return f"https://drive.google.com/file/d/{file_id}/view"

    def _folder_has_public_link(self, access_token: str, folder_id: str) -> bool:
        data = self._request_json(
            method="GET",
            url=(
                f"https://www.googleapis.com/drive/v3/files/{folder_id}/permissions?"
                + parse.urlencode(
                    {
                        "fields": "permissions(id,type,role,allowFileDiscovery)",
                        "supportsAllDrives": "true",
                    }
                )
            ),
            headers={"Authorization": f"Bearer {access_token}"},
        )
        permissions = data.get("permissions", [])
        return any(permission.get("type") == "anyone" for permission in permissions)

    def _build_multipart_body(self, local_path: Path, metadata: dict[str, object]) -> tuple[bytes, str]:
        boundary = f"photo-processor-{uuid.uuid4().hex}"
        mime_type = mimetypes.guess_type(local_path.name)[0] or "application/octet-stream"
        file_bytes = local_path.read_bytes()
        parts = [
            f"--{boundary}\r\n"
            "Content-Type: application/json; charset=UTF-8\r\n\r\n"
            f"{json.dumps(metadata)}\r\n",
            f"--{boundary}\r\n"
            f"Content-Type: {mime_type}\r\n\r\n",
        ]
        body = "".join(parts).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")
        return body, f"multipart/related; boundary={boundary}"

    def _request_json(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None = None,
    ) -> dict[str, object]:
        status_code, payload = self.requester(method, url, headers, body)
        if status_code >= 400:
            message = payload.decode("utf-8", errors="replace")
            if status_code in (401, 403):
                raise RuntimeError(
                    "Google Drive request was rejected by Google. "
                    "The saved connection may be missing required Drive permissions. "
                    "Disconnect Google Drive and connect it again, then retry. "
                    f"Details: {message}"
                )
            raise RuntimeError(f"Google Drive request failed with status {status_code}: {message}")
        if not payload:
            return {}
        return json.loads(payload.decode("utf-8"))

    def _default_requester(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None,
    ) -> tuple[int, bytes]:
        request_obj = request.Request(url, data=body, method=method, headers=headers)
        try:
            with request.urlopen(request_obj) as response:
                return response.getcode(), response.read()
        except HTTPError as exc:
            return exc.code, exc.read()
        except URLError as exc:  # pragma: no cover - network/environment dependent
            raise RuntimeError(f"Google Drive request failed: {exc.reason}") from exc

    def _remote_path(self, folder_id: str | None, filename: str) -> str:
        if not folder_id:
            return filename
        return f"{folder_id}/{filename}"
