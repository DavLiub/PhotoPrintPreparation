import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.core.orientation import choose_target_frame, should_rotate_for_better_fit


class OrientationTestCase(unittest.TestCase):
    def test_rotate_for_better_fit_when_portrait_matches_better(self) -> None:
        self.assertIs(should_rotate_for_better_fit(1000, 1500, 1500, 1000), True)

    def test_choose_target_frame_can_swap_dimensions(self) -> None:
        self.assertEqual(
            choose_target_frame(1500, 1000, 1000, 1500, True, True),
            (1000, 1500),
        )

    def test_choose_target_frame_keeps_original_when_rotation_disabled(self) -> None:
        self.assertEqual(
            choose_target_frame(1500, 1000, 1000, 1500, True, False),
            (1500, 1000),
        )
