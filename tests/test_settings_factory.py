from argparse import Namespace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.api.settings_factory import build_settings_from_args
from photo_processor.core.output_policy import ConflictStrategy
from photo_processor.core.settings import ResizeMode, Units


class SettingsFactoryTestCase(unittest.TestCase):
    def test_factory_uses_defaults_without_preset(self) -> None:
        settings = build_settings_from_args(
            Namespace(
                source="C:\\Photos",
                output=None,
                preset=None,
                width=None,
                height=None,
                units=None,
                dpi=None,
                resize_mode=None,
                max_file_size_mb=None,
                suffix="_processed",
                conflict_strategy=ConflictStrategy.ADD_COUNTER.value,
            )
        )

        self.assertEqual(settings.width, 1500)
        self.assertEqual(settings.height, 1000)
        self.assertEqual(settings.units, Units.PIXELS)
        self.assertEqual(settings.resize_mode, ResizeMode.CONTAIN)

    def test_factory_uses_preset_values(self) -> None:
        settings = build_settings_from_args(
            Namespace(
                source="C:\\Photos",
                output=None,
                preset="print_10x15",
                width=None,
                height=None,
                units=None,
                dpi=None,
                resize_mode=None,
                max_file_size_mb=None,
                suffix="_processed",
                conflict_strategy=ConflictStrategy.ADD_COUNTER.value,
            )
        )

        self.assertEqual(settings.width, 15)
        self.assertEqual(settings.height, 10)
        self.assertEqual(settings.units, Units.CENTIMETERS)
        self.assertEqual(settings.dpi, 300)
        self.assertEqual(settings.resize_mode, ResizeMode.CONTAIN)
        self.assertEqual(settings.max_file_size_mb, 5.0)

    def test_factory_allows_cli_values_to_override_preset(self) -> None:
        settings = build_settings_from_args(
            Namespace(
                source="C:\\Photos",
                output=None,
                preset="print_10x15",
                width=20,
                height=13,
                units=Units.CENTIMETERS.value,
                dpi=200,
                resize_mode=ResizeMode.COVER.value,
                max_file_size_mb=3.0,
                suffix="_done",
                conflict_strategy=ConflictStrategy.SKIP.value,
            )
        )

        self.assertEqual(settings.width, 20)
        self.assertEqual(settings.height, 13)
        self.assertEqual(settings.units, Units.CENTIMETERS)
        self.assertEqual(settings.dpi, 200)
        self.assertEqual(settings.resize_mode, ResizeMode.COVER)
        self.assertEqual(settings.max_file_size_mb, 3.0)
        self.assertEqual(settings.output_policy.filename_suffix, "_done")
        self.assertEqual(settings.output_policy.conflict_strategy, ConflictStrategy.SKIP)
