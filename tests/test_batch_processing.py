import sys
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.app.use_cases.batch_processing import BatchProcessingUseCase
from photo_processor.core.settings import ProcessingSettings
from photo_processor.core.single_image_result import SingleImageResult


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

    def test_batch_continues_after_one_file_failure(self) -> None:
        source_dir = Path(self._testMethodName)
        output_dir = source_dir / "out"
        source_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, source_dir)

        bad_source = source_dir / "a.jpg"
        good_source = source_dir / "b.png"
        bad_source.write_bytes(b"bad")
        good_source.write_bytes(b"good")

        settings = ProcessingSettings(source_folder=source_dir, output_folder=output_dir)

        def fake_process(task):
            if task.source_path.name == "a.jpg":
                raise RuntimeError("broken file")
            return SingleImageResult(
                source_path=task.source_path,
                output_path=task.output_path,
                success=True,
            )

        with patch("photo_processor.app.use_cases.batch_processing.ImageProcessor.process", side_effect=fake_process):
            result = BatchProcessingUseCase(settings).run()

        self.assertEqual(result.found_files, 2)
        self.assertEqual(result.processed_files, 1)
        self.assertEqual(result.error_files, 1)
        self.assertEqual(len(result.items), 2)
        self.assertTrue(any(item.success for item in result.items))
        self.assertTrue(any((item.error_message or "") == "broken file" for item in result.items))


def _cleanup_tree(path: Path) -> None:
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_file():
            child.unlink()
        else:
            child.rmdir()
    path.rmdir()
