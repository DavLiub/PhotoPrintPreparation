from pathlib import Path
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.core.output_policy import ConflictStrategy, OutputFormat, OutputPolicy
from photo_processor.infra.filesystem.output_path_builder import build_output_path


class OutputPathBuilderTestCase(unittest.TestCase):
    def test_build_output_path_adds_suffix(self) -> None:
        tmp_path = Path(self._testMethodName)
        tmp_path.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, tmp_path)

        source = tmp_path / "IMG_1234.jpg"
        source.write_text("x", encoding="utf-8")

        output = build_output_path(
            source,
            tmp_path,
            OutputPolicy(filename_suffix="_processed", output_format=OutputFormat.JPEG),
        )

        self.assertEqual(output, tmp_path / "IMG_1234_processed.jpg")

    def test_build_output_path_adds_counter_when_target_exists(self) -> None:
        tmp_path = Path(self._testMethodName)
        tmp_path.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, tmp_path)

        source = tmp_path / "IMG_1234.jpg"
        source.write_text("x", encoding="utf-8")
        existing = tmp_path / "IMG_1234_processed.jpg"
        existing.write_text("x", encoding="utf-8")

        output = build_output_path(
            source,
            tmp_path,
            OutputPolicy(filename_suffix="_processed", output_format=OutputFormat.JPEG),
        )

        self.assertEqual(output, tmp_path / "IMG_1234_processed_1.jpg")

    def test_build_output_path_can_overwrite_existing_target(self) -> None:
        tmp_path = Path(self._testMethodName)
        tmp_path.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, tmp_path)

        source = tmp_path / "IMG_1234.jpg"
        source.write_text("x", encoding="utf-8")
        existing = tmp_path / "IMG_1234_processed.jpg"
        existing.write_text("x", encoding="utf-8")

        output = build_output_path(
            source,
            tmp_path,
            OutputPolicy(
                filename_suffix="_processed",
                output_format=OutputFormat.JPEG,
                conflict_strategy=ConflictStrategy.OVERWRITE,
            ),
        )

        self.assertEqual(output, existing)

    def test_build_output_path_can_skip_existing_target(self) -> None:
        tmp_path = Path(self._testMethodName)
        tmp_path.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, tmp_path)

        source = tmp_path / "IMG_1234.jpg"
        source.write_text("x", encoding="utf-8")
        existing = tmp_path / "IMG_1234_processed.jpg"
        existing.write_text("x", encoding="utf-8")

        output = build_output_path(
            source,
            tmp_path,
            OutputPolicy(
                filename_suffix="_processed",
                output_format=OutputFormat.JPEG,
                conflict_strategy=ConflictStrategy.SKIP,
            ),
        )

        self.assertIsNone(output)


def _cleanup_tree(path: Path) -> None:
    for child in path.iterdir():
        child.unlink()
    path.rmdir()
