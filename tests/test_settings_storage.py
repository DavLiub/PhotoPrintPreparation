import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.core.settings_snapshot import SettingsSnapshot
from photo_processor.infra.settings_storage.json_settings_storage import JsonSettingsStorage


class JsonSettingsStorageTestCase(unittest.TestCase):
    def test_load_returns_none_when_file_is_missing(self) -> None:
        work_dir = Path(self._testMethodName)
        storage = JsonSettingsStorage(work_dir / "settings.json")
        self.addCleanup(_cleanup_tree, work_dir, create=False)

        snapshot = storage.load()

        self.assertIsNone(snapshot)

    def test_save_and_load_snapshot(self) -> None:
        work_dir = Path(self._testMethodName)
        settings_path = work_dir / "config" / "settings.json"
        storage = JsonSettingsStorage(settings_path)
        self.addCleanup(_cleanup_tree, work_dir, create=False)

        expected = SettingsSnapshot(
            preset_id="print_10x15",
            source_folder="C:\\Photos",
            output_folder="C:\\Photos\\processed",
            width=15,
            height=10,
            units="centimeters",
            dpi=300,
            resize_mode="contain",
            max_file_size_mb=5.0,
            filename_suffix="_processed",
            conflict_strategy="add_counter",
            source_formats=(".jpg", ".png"),
            output_format="jpeg",
        )

        storage.save(expected)

        self.assertTrue(settings_path.exists())
        self.assertEqual(storage.load(), expected)
        data = json.loads(settings_path.read_text(encoding="utf-8"))
        self.assertEqual(data["preset_id"], "print_10x15")


def _cleanup_tree(path: Path, create: bool) -> None:
    if create:
        path.mkdir(exist_ok=True)
    if not path.exists():
        return
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_file():
            child.unlink()
        else:
            child.rmdir()
    path.rmdir()
