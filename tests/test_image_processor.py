import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.core.image_task import ImageTask
from photo_processor.core.settings import ProcessingSettings, ResizeMode
from photo_processor.infra.imaging.image_processor import ImageProcessor

PILLOW_AVAILABLE = importlib.util.find_spec("PIL") is not None

if PILLOW_AVAILABLE:
    from PIL import Image


@unittest.skipUnless(PILLOW_AVAILABLE, "Pillow is required for image processing tests")
class ImageProcessorTestCase(unittest.TestCase):
    def test_process_creates_jpeg_in_target_frame(self) -> None:
        source_dir = Path(self._testMethodName)
        output_dir = source_dir / "out"
        source_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, source_dir)

        source_path = source_dir / "sample.png"
        output_path = output_dir / "sample_processed.jpg"
        Image.new("RGB", (1200, 800), (50, 100, 150)).save(source_path, format="PNG")

        settings = ProcessingSettings(
            source_folder=source_dir,
            output_folder=output_dir,
            width=1500,
            height=1000,
            resize_mode=ResizeMode.CONTAIN,
            max_file_size_mb=1.0,
        )

        result_info = ImageProcessor(settings).process(ImageTask(source_path=source_path, output_path=output_path))

        self.assertTrue(output_path.exists())
        self.assertTrue(result_info.success)
        self.assertEqual(result_info.target_size, (1500, 1000))
        self.assertEqual(result_info.output_size, (1500, 1000))
        self.assertIsNotNone(result_info.output_file_size_bytes)
        self.assertIsNotNone(result_info.output_quality)
        with Image.open(output_path) as result:
            self.assertEqual(result.format, "JPEG")
            self.assertEqual(result.size, (1500, 1000))

    def test_process_swaps_target_frame_for_portrait_input(self) -> None:
        source_dir = Path(self._testMethodName)
        output_dir = source_dir / "out"
        source_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, source_dir)

        source_path = source_dir / "portrait.png"
        output_path = output_dir / "portrait_processed.jpg"
        Image.new("RGB", (800, 1200), (120, 80, 60)).save(source_path, format="PNG")

        settings = ProcessingSettings(
            source_folder=source_dir,
            output_folder=output_dir,
            width=1500,
            height=1000,
            resize_mode=ResizeMode.CONTAIN,
            max_file_size_mb=1.0,
        )

        result_info = ImageProcessor(settings).process(ImageTask(source_path=source_path, output_path=output_path))

        self.assertEqual(result_info.target_size, (1000, 1500))
        with Image.open(output_path) as result:
            self.assertEqual(result.size, (1000, 1500))


def _cleanup_tree(path: Path) -> None:
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_file():
            child.unlink()
        else:
            child.rmdir()
    path.rmdir()
