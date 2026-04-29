import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.app.use_cases.batch_processing import BatchProcessingUseCase
from photo_processor.core.settings import ProcessingSettings


class BatchProcessingTestCase(unittest.TestCase):
    def test_dry_run_collects_per_file_items(self) -> None:
        source_dir = Path(self._testMethodName)
        output_dir = source_dir / "out"
        source_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, source_dir)

        (source_dir / "a.jpg").write_bytes(b"jpg")
        (source_dir / "b.png").write_bytes(b"png")

        settings = ProcessingSettings(source_folder=source_dir, output_folder=output_dir)

        result = BatchProcessingUseCase(settings).run(dry_run=True)

        self.assertEqual(result.found_files, 2)
        self.assertEqual(result.processed_files, 2)
        self.assertEqual(result.error_files, 0)
        self.assertEqual(len(result.items), 2)
        self.assertTrue(all(item.success for item in result.items))
        self.assertTrue(any("Dry run" in warning for item in result.items for warning in item.warnings))

    def test_missing_source_folder_returns_failed_item(self) -> None:
        source_dir = Path(self._testMethodName)
        output_dir = source_dir / "out"
        settings = ProcessingSettings(source_folder=source_dir, output_folder=output_dir)

        result = BatchProcessingUseCase(settings).run()

        self.assertEqual(result.error_files, 1)
        self.assertEqual(len(result.items), 1)
        self.assertFalse(result.items[0].success)
        self.assertIn("does not exist", result.items[0].error_message or "")


def _cleanup_tree(path: Path) -> None:
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_file():
            child.unlink()
        else:
            child.rmdir()
    path.rmdir()
