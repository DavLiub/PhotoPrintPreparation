import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.infra.settings_storage.storage_paths import resolve_settings_path


class StoragePathsTestCase(unittest.TestCase):
    def test_resolve_settings_path_uses_programdata_when_available(self) -> None:
        with patch.dict(os.environ, {"ProgramData": r"C:\ProgramData"}, clear=False):
            path = resolve_settings_path()

        self.assertEqual(path, Path(r"C:\ProgramData") / "PhotoPrintPreparation" / "settings.json")
