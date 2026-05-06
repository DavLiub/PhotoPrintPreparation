from argparse import Namespace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.api.settings_factory import build_settings_from_args, build_snapshot_from_settings
from photo_processor.core.cloud_upload import CloudProvider
from photo_processor.core.output_policy import ConflictStrategy, OutputFormat
from photo_processor.core.settings import CropAnchor, ResizeMode, SUPPORTED_INPUT_FORMATS, Units
from photo_processor.core.settings_snapshot import SettingsSnapshot


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
                upload_provider=None,
                upload_remote_folder=None,
                upload_create_share_link=None,
                upload_delete_local_after_upload=None,
                upload_overwrite_remote=None,
            )
        )

        self.assertEqual(settings.width, 1500)
        self.assertEqual(settings.height, 1000)
        self.assertEqual(settings.units, Units.PIXELS)
        self.assertEqual(settings.resize_mode, ResizeMode.CONTAIN)
        self.assertEqual(settings.crop_anchor, CropAnchor.TOP_LEFT)
        self.assertEqual(settings.source_formats, SUPPORTED_INPUT_FORMATS)
        self.assertEqual(settings.output_policy.output_format, OutputFormat.JPEG)
        self.assertFalse(settings.cloud_upload.enabled)

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
                upload_provider=None,
                upload_remote_folder=None,
                upload_create_share_link=None,
                upload_delete_local_after_upload=None,
                upload_overwrite_remote=None,
            )
        )

        self.assertEqual(settings.width, 15)
        self.assertEqual(settings.height, 10)
        self.assertEqual(settings.units, Units.CENTIMETERS)
        self.assertEqual(settings.dpi, 300)
        self.assertTrue(settings.auto_rotate)
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
                resize_mode=ResizeMode.FIT_HEIGHT.value,
                max_file_size_mb=3.0,
                suffix="_done",
                conflict_strategy=ConflictStrategy.SKIP.value,
                upload_provider=None,
                upload_remote_folder=None,
                upload_create_share_link=None,
                upload_delete_local_after_upload=None,
                upload_overwrite_remote=None,
            )
        )

        self.assertEqual(settings.width, 20)
        self.assertEqual(settings.height, 13)
        self.assertEqual(settings.units, Units.CENTIMETERS)
        self.assertEqual(settings.dpi, 200)
        self.assertEqual(settings.resize_mode, ResizeMode.FIT_HEIGHT)
        self.assertEqual(settings.max_file_size_mb, 3.0)
        self.assertEqual(settings.output_policy.filename_suffix, "_done")
        self.assertEqual(settings.output_policy.conflict_strategy, ConflictStrategy.SKIP)

    def test_factory_uses_saved_snapshot_when_cli_and_preset_are_missing(self) -> None:
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
                suffix=None,
                conflict_strategy=None,
                upload_provider=None,
                upload_remote_folder=None,
                upload_create_share_link=None,
                upload_delete_local_after_upload=None,
                upload_overwrite_remote=None,
            ),
            saved_snapshot=SettingsSnapshot(
                width=1600,
                height=1200,
                units=Units.PIXELS.value,
                dpi=200,
                auto_rotate=False,
                resize_mode="cover",
                crop_anchor=CropAnchor.CENTER.value,
                max_file_size_mb=1.2,
                filename_suffix="_saved",
                conflict_strategy=ConflictStrategy.SKIP.value,
                source_formats=(".jpg", ".png"),
                output_format=OutputFormat.JPEG.value,
                cloud_upload_enabled=True,
                cloud_provider=CloudProvider.GOOGLE_DRIVE.value,
                cloud_connection_id="google-primary",
                cloud_account_email="user@example.com",
                cloud_remote_folder="folder-1",
                cloud_remote_folder_share_link="https://drive.google.com/drive/folders/folder-1?usp=sharing",
                cloud_create_share_link=True,
            ),
        )

        self.assertEqual(settings.width, 1600)
        self.assertEqual(settings.height, 1200)
        self.assertEqual(settings.dpi, 200)
        self.assertFalse(settings.auto_rotate)
        self.assertEqual(settings.resize_mode, ResizeMode.CONTAIN)
        self.assertEqual(settings.crop_anchor, CropAnchor.CENTER)
        self.assertEqual(settings.output_policy.filename_suffix, "_saved")
        self.assertEqual(settings.output_policy.conflict_strategy, ConflictStrategy.SKIP)
        self.assertEqual(settings.source_formats, (".jpg", ".png"))
        self.assertEqual(settings.output_policy.output_format, OutputFormat.JPEG)
        self.assertTrue(settings.cloud_upload.enabled)
        self.assertEqual(settings.cloud_upload.provider, CloudProvider.GOOGLE_DRIVE)
        self.assertEqual(settings.cloud_upload.connection_id, "google-primary")
        self.assertEqual(settings.cloud_upload.account_email, "user@example.com")
        self.assertEqual(settings.cloud_upload.remote_folder, "folder-1")
        self.assertEqual(
            settings.cloud_upload.remote_folder_share_link,
            "https://drive.google.com/drive/folders/folder-1?usp=sharing",
        )
        self.assertTrue(settings.cloud_upload.create_share_link)

    def test_build_snapshot_from_settings_serializes_runtime_values(self) -> None:
        settings = build_settings_from_args(
            Namespace(
                source="C:\\Photos",
                output="C:\\Photos\\processed",
                preset="photo_report",
                width=1800,
                height=1100,
                units=Units.PIXELS.value,
                dpi=300,
                resize_mode=ResizeMode.FIT_WIDTH.value,
                max_file_size_mb=2.5,
                suffix="_done",
                conflict_strategy=ConflictStrategy.OVERWRITE.value,
                upload_provider=CloudProvider.GOOGLE_DRIVE.value,
                upload_remote_folder="folder-2",
                upload_create_share_link=True,
                upload_delete_local_after_upload=False,
                upload_overwrite_remote=True,
            )
        )

        snapshot = build_snapshot_from_settings(settings, "photo_report")

        self.assertEqual(snapshot.preset_id, "photo_report")
        self.assertEqual(snapshot.width, 1800)
        self.assertEqual(snapshot.height, 1100)
        self.assertTrue(snapshot.auto_rotate)
        self.assertEqual(snapshot.resize_mode, ResizeMode.FIT_WIDTH.value)
        self.assertEqual(snapshot.crop_anchor, CropAnchor.TOP_LEFT.value)
        self.assertEqual(snapshot.filename_suffix, "_done")
        self.assertEqual(snapshot.conflict_strategy, ConflictStrategy.OVERWRITE.value)
        self.assertEqual(snapshot.source_formats, SUPPORTED_INPUT_FORMATS)
        self.assertEqual(snapshot.output_format, OutputFormat.JPEG.value)
        self.assertTrue(snapshot.cloud_upload_enabled)
        self.assertEqual(snapshot.cloud_provider, CloudProvider.GOOGLE_DRIVE.value)
        self.assertIsNone(snapshot.cloud_connection_id)
        self.assertIsNone(snapshot.cloud_account_email)
        self.assertEqual(snapshot.cloud_remote_folder, "folder-2")
        self.assertTrue(snapshot.cloud_create_share_link)
        self.assertFalse(snapshot.cloud_delete_local_after_upload)
        self.assertTrue(snapshot.cloud_overwrite_remote)
