import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.core.resize_rules import (
    calculate_contain_size,
    calculate_fit_height_size,
    calculate_fit_width_size,
)


class ResizeRulesTestCase(unittest.TestCase):
    def test_contain_plan(self) -> None:
        plan = calculate_contain_size(30, 22, 15, 10)
        self.assertEqual((plan.resized_width, plan.resized_height), (14, 10))
        self.assertEqual(plan.padding, (0, 0, 1, 0))

    def test_fit_width_plan(self) -> None:
        plan = calculate_fit_width_size(30, 22, 15, 10)
        self.assertEqual((plan.resized_width, plan.resized_height), (15, 11))
        self.assertEqual(plan.crop_box, (0, 0, 15, 10))

    def test_fit_height_plan(self) -> None:
        plan = calculate_fit_height_size(30, 22, 15, 10)
        self.assertEqual((plan.resized_width, plan.resized_height), (14, 10))
        self.assertEqual(plan.padding, (0, 0, 1, 0))
        self.assertIsNone(plan.crop_box)
