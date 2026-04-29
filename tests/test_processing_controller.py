import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.app.controllers.processing_controller import ProcessingController
from photo_processor.core.settings import ProcessingSettings


class ProcessingControllerTestCase(unittest.TestCase):
    def test_run_returns_result_and_report(self) -> None:
        source_dir = Path(self._testMethodName)
        output_dir = source_dir / "out"
        source_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, source_dir)

        (source_dir / "a.jpg").write_bytes(b"jpg")
        (source_dir / "b.png").write_bytes(b"png")

        execution = ProcessingController().run(
            ProcessingSettings(source_folder=source_dir, output_folder=output_dir),
            dry_run=True,
        )

        self.assertEqual(execution.result.found_files, 2)
        self.assertEqual(execution.report.found_files, 2)
        self.assertEqual(execution.report.processed_files, 2)
        self.assertTrue(any("Found files" in line for line in execution.report.summary_lines))


def _cleanup_tree(path: Path) -> None:
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_file():
            child.unlink()
        else:
            child.rmdir()
    path.rmdir()
