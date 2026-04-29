import importlib.util
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.infra.imaging import jpeg_optimizer
from photo_processor.infra.imaging.jpeg_optimizer import save_jpeg_with_limit

PILLOW_AVAILABLE = importlib.util.find_spec("PIL") is not None

if PILLOW_AVAILABLE:
    from PIL import Image


@unittest.skipUnless(PILLOW_AVAILABLE, "Pillow is required for jpeg optimizer tests")
class JpegOptimizerTestCase(unittest.TestCase):
    def test_optimizer_can_reduce_quality_under_limit(self) -> None:
        work_dir = Path(self._testMethodName)
        work_dir.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, work_dir)

        output_path = work_dir / "quality.jpg"
        image = Image.new("RGB", (10, 10), (100, 120, 140))

        def fake_encode(_image, quality: int) -> bytes:
            if quality >= 80:
                return b"x" * 150
            return b"x" * 80

        with patch.object(jpeg_optimizer, "_encode_jpeg", side_effect=fake_encode):
            result = save_jpeg_with_limit(image, output_path, max_file_size_mb=0.0001)

        self.assertTrue(output_path.exists())
        self.assertLessEqual(result.file_size_bytes, int(0.0001 * 1024 * 1024))
        self.assertEqual(result.quality, 75)
        self.assertFalse(result.was_dimension_reduced)

    def test_optimizer_reduces_dimensions_when_quality_is_not_enough(self) -> None:
        work_dir = Path(self._testMethodName)
        work_dir.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, work_dir)

        output_path = work_dir / "dimensions.jpg"
        image = Image.effect_noise((1800, 1800), 100).convert("RGB")

        result = save_jpeg_with_limit(image, output_path, max_file_size_mb=0.02)

        self.assertTrue(output_path.exists())
        self.assertTrue(result.was_dimension_reduced)
        self.assertLess(result.output_size[0], 1800)
        self.assertLess(result.output_size[1], 1800)
        self.assertLessEqual(result.file_size_bytes, int(0.02 * 1024 * 1024))


def _cleanup_tree(path: Path) -> None:
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_file():
            child.unlink()
        else:
            child.rmdir()
    path.rmdir()
