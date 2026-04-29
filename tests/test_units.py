import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.core.units import centimeters_to_pixels, pixels_to_centimeters


class UnitsTestCase(unittest.TestCase):
    def test_centimeters_to_pixels(self) -> None:
        self.assertEqual(centimeters_to_pixels(15, 300), 1772)

    def test_pixels_to_centimeters(self) -> None:
        self.assertEqual(round(pixels_to_centimeters(1772, 300), 1), 15.0)
