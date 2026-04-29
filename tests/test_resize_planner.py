import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.core.settings import ProcessingSettings, ResizeMode
from photo_processor.infra.imaging.resize_planner import build_resize_plan


class ResizePlannerTestCase(unittest.TestCase):
    def test_planner_swaps_target_frame_for_portrait_source(self) -> None:
        settings = ProcessingSettings(
            source_folder=Path("input"),
            output_folder=Path("output"),
            width=1500,
            height=1000,
            resize_mode=ResizeMode.CONTAIN,
        )

        target_width, target_height, plan = build_resize_plan(settings, 1000, 1500)

        self.assertEqual((target_width, target_height), (1000, 1500))
        self.assertEqual((plan.resized_width, plan.resized_height), (1000, 1500))

    def test_planner_uses_fit_height_math(self) -> None:
        settings = ProcessingSettings(
            source_folder=Path("input"),
            output_folder=Path("output"),
            width=1500,
            height=1000,
            resize_mode=ResizeMode.FIT_HEIGHT,
        )

        target_width, target_height, plan = build_resize_plan(settings, 3000, 2200)

        self.assertEqual((target_width, target_height), (1500, 1000))
        self.assertEqual((plan.resized_width, plan.resized_height), (1364, 1000))
        self.assertIsNone(plan.crop_box)
