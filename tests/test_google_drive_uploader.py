import json
import sys
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.infra.cloud.google_drive_uploader import (
    GoogleDriveCredentials,
    GoogleDriveUploader,
)


class GoogleDriveUploaderFolderTestCase(unittest.TestCase):
    def test_list_folders_reads_root_children(self) -> None:
        calls: list[tuple[str, str]] = []

        def requester(method: str, url: str, headers: dict[str, str], body: bytes | None) -> tuple[int, bytes]:
            calls.append((method, url))
            if "oauth2.googleapis.com/token" in url:
                return 200, json.dumps({"access_token": "token-123"}).encode("utf-8")
            query = parse_qs(urlparse(url).query)
            self.assertIn("'root' in parents", query["q"][0])
            return 200, json.dumps(
                {
                    "files": [
                        {"id": "folder-a", "name": "Albums", "parents": ["root"]},
                        {"id": "folder-b", "name": "Prints", "parents": ["root"]},
                    ]
                }
            ).encode("utf-8")

        uploader = GoogleDriveUploader(
            GoogleDriveCredentials(client_id="client-123", refresh_token="refresh-token"),
            requester=requester,
        )

        folders = uploader.list_folders()

        self.assertEqual(
            [(folder.folder_id, folder.name, folder.parent_id) for folder in folders],
            [("folder-a", "Albums", "root"), ("folder-b", "Prints", "root")],
        )
        self.assertEqual(len(calls), 2)

    def test_get_folder_returns_root_without_network(self) -> None:
        uploader = GoogleDriveUploader(
            GoogleDriveCredentials(client_id="client-123", refresh_token="refresh-token"),
            requester=lambda *_args: (_ for _ in ()).throw(AssertionError("network should not be used")),
        )

        folder = uploader.get_folder("root")

        self.assertEqual(folder.folder_id, "root")
        self.assertEqual(folder.name, "My Drive")
        self.assertIsNone(folder.parent_id)

    def test_get_folder_path_builds_human_readable_path(self) -> None:
        def requester(method: str, url: str, headers: dict[str, str], body: bytes | None) -> tuple[int, bytes]:
            if "oauth2.googleapis.com/token" in url:
                return 200, json.dumps({"access_token": "token-123"}).encode("utf-8")
            if "/files/folder-c?" in url:
                return 200, json.dumps({"id": "folder-c", "name": "2026", "parents": ["folder-b"]}).encode("utf-8")
            if "/files/folder-b?" in url:
                return 200, json.dumps({"id": "folder-b", "name": "Prints", "parents": ["root"]}).encode("utf-8")
            raise AssertionError(f"Unexpected URL: {url}")

        uploader = GoogleDriveUploader(
            GoogleDriveCredentials(client_id="client-123", refresh_token="refresh-token"),
            requester=requester,
        )

        path = uploader.get_folder_path("folder-c")

        self.assertEqual(path, "My Drive / Prints / 2026")

    def test_get_or_create_folder_share_link_reuses_existing_public_access(self) -> None:
        calls: list[tuple[str, str]] = []

        def requester(method: str, url: str, headers: dict[str, str], body: bytes | None) -> tuple[int, bytes]:
            calls.append((method, url))
            if "oauth2.googleapis.com/token" in url:
                return 200, json.dumps({"access_token": "token-123"}).encode("utf-8")
            if "/permissions?" in url and method == "GET":
                return 200, json.dumps({"permissions": [{"id": "perm-1", "type": "anyone", "role": "reader"}]}).encode(
                    "utf-8"
                )
            raise AssertionError(f"Unexpected URL: {url}")

        uploader = GoogleDriveUploader(
            GoogleDriveCredentials(client_id="client-123", refresh_token="refresh-token"),
            requester=requester,
        )

        share_link = uploader.get_or_create_folder_share_link("folder-shared")

        self.assertEqual(share_link, "https://drive.google.com/drive/folders/folder-shared?usp=sharing")
        self.assertEqual(len(calls), 2)
        self.assertFalse(any(method == "POST" and "/permissions" in url for method, url in calls))

    def test_create_folder_posts_google_drive_folder_metadata(self) -> None:
        calls: list[tuple[str, str, bytes | None]] = []

        def requester(method: str, url: str, headers: dict[str, str], body: bytes | None) -> tuple[int, bytes]:
            calls.append((method, url, body))
            if "oauth2.googleapis.com/token" in url:
                return 200, json.dumps({"access_token": "token-123"}).encode("utf-8")
            if method == "POST" and "drive/v3/files?supportsAllDrives=true&fields=id,name,parents" in url:
                payload = json.loads((body or b"{}").decode("utf-8"))
                self.assertEqual(payload["name"], "New Folder")
                self.assertEqual(payload["mimeType"], "application/vnd.google-apps.folder")
                self.assertEqual(payload["parents"], ["folder-parent"])
                return 200, json.dumps({"id": "folder-new", "name": "New Folder", "parents": ["folder-parent"]}).encode(
                    "utf-8"
                )
            raise AssertionError(f"Unexpected URL: {url}")

        uploader = GoogleDriveUploader(
            GoogleDriveCredentials(client_id="client-123", refresh_token="refresh-token"),
            requester=requester,
        )

        folder = uploader.create_folder("New Folder", "folder-parent")

        self.assertEqual(folder.folder_id, "folder-new")
        self.assertEqual(folder.name, "New Folder")
        self.assertEqual(folder.parent_id, "folder-parent")
        self.assertEqual(len(calls), 2)

    def test_folder_requests_reuse_cached_access_token_and_folder_metadata(self) -> None:
        calls: list[tuple[str, str]] = []

        def requester(method: str, url: str, headers: dict[str, str], body: bytes | None) -> tuple[int, bytes]:
            calls.append((method, url))
            if "oauth2.googleapis.com/token" in url:
                return 200, json.dumps({"access_token": "token-123", "expires_in": 3600}).encode("utf-8")
            if "/files/folder-c?" in url:
                return 200, json.dumps({"id": "folder-c", "name": "2026", "parents": ["folder-b"]}).encode("utf-8")
            if "/files/folder-b?" in url:
                return 200, json.dumps({"id": "folder-b", "name": "Prints", "parents": ["root"]}).encode("utf-8")
            raise AssertionError(f"Unexpected URL: {url}")

        uploader = GoogleDriveUploader(
            GoogleDriveCredentials(client_id="client-123", refresh_token="refresh-token"),
            requester=requester,
        )

        path_one = uploader.get_folder_path("folder-c")
        path_two = uploader.get_folder_path("folder-c")

        self.assertEqual(path_one, "My Drive / Prints / 2026")
        self.assertEqual(path_two, "My Drive / Prints / 2026")
        token_calls = [url for _method, url in calls if "oauth2.googleapis.com/token" in url]
        self.assertEqual(len(token_calls), 1)


if __name__ == "__main__":
    unittest.main()
