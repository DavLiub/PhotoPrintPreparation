import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.config import cloud_oauth


class CloudOAuthTestCase(unittest.TestCase):
    def test_get_google_drive_client_id_uses_embedded_value_when_env_is_missing(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(cloud_oauth, "EMBEDDED_GOOGLE_DRIVE_CLIENT_ID", "embedded-client"):
                client_id = cloud_oauth.get_google_drive_client_id()

        self.assertEqual(client_id, "embedded-client")

    def test_get_google_drive_client_secret_uses_embedded_value_when_env_is_missing(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(cloud_oauth, "EMBEDDED_GOOGLE_DRIVE_CLIENT_SECRET", "embedded-secret"):
                client_secret = cloud_oauth.get_google_drive_client_secret()

        self.assertEqual(client_secret, "embedded-secret")


if __name__ == "__main__":
    unittest.main()
