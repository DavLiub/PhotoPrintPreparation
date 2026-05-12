import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.bootstrap.build_embedded_oauth import build_embedded_oauth_module


class BuildEmbeddedOAuthTestCase(unittest.TestCase):
    def test_build_embedded_oauth_module_writes_python_config_file(self) -> None:
        fake_file = Path("C:/repo/src/photo_processor/bootstrap/build_embedded_oauth.py")
        expected_target = Path("C:/repo/src/photo_processor/config/cloud_oauth_embedded.py")
        write_mock = MagicMock()

        with patch.dict(
            os.environ,
            {
                "PHOTO_PROCESSOR_GDRIVE_CLIENT_ID": "client-id",
                "PHOTO_PROCESSOR_GDRIVE_CLIENT_SECRET": "client-secret",
            },
            clear=False,
        ):
            with patch("photo_processor.bootstrap.build_embedded_oauth.load_cloud_oauth_env"):
                with patch("photo_processor.bootstrap.build_embedded_oauth.__file__", str(fake_file)):
                    with patch("pathlib.Path.write_text", write_mock):
                        written_path = build_embedded_oauth_module()

        self.assertEqual(written_path, expected_target)
        self.assertEqual(write_mock.call_count, 1)
        written_content = write_mock.call_args.args[0]
        self.assertIn("GOOGLE_DRIVE_CLIENT_ID = 'client-id'", written_content)
        self.assertIn("GOOGLE_DRIVE_CLIENT_SECRET = 'client-secret'", written_content)


if __name__ == "__main__":
    unittest.main()
