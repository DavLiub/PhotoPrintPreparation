from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.bootstrap.env_loader import resolve_cloud_oauth_env_paths


class EnvLoaderTestCase(unittest.TestCase):
    def test_resolve_cloud_oauth_env_paths_includes_current_workdir_and_exe_dir_when_frozen(self) -> None:
        fake_cwd = Path("C:/Portable/App")
        fake_exe = fake_cwd / "PhotoPrintPreparation.exe"

        with patch("photo_processor.bootstrap.env_loader.Path.cwd", return_value=fake_cwd):
            with patch("photo_processor.bootstrap.env_loader.sys", frozen=True, executable=str(fake_exe), _MEIPASS=None):
                paths = resolve_cloud_oauth_env_paths()

        self.assertIn((fake_cwd / "config" / "cloud_oauth.env").resolve(strict=False), paths)
        self.assertIn((fake_cwd / "cloud_oauth.env").resolve(strict=False), paths)


if __name__ == "__main__":
    unittest.main()
