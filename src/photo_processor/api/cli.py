from __future__ import annotations

import argparse

from photo_processor.api.settings_factory import build_settings_from_args, build_snapshot_from_settings
from photo_processor.app.controllers.processing_controller import ProcessingController
from photo_processor.bootstrap.env_loader import load_cloud_oauth_env
from photo_processor.config.presets import get_preset_ids
from photo_processor.core.cloud_upload import CloudProvider
from photo_processor.core.output_policy import ConflictStrategy
from photo_processor.core.settings import ResizeMode, Units
from photo_processor.infra.cloud.uploader_factory import build_cloud_uploader
from photo_processor.infra.settings_storage.json_settings_storage import JsonSettingsStorage
from photo_processor.infra.settings_storage.storage_paths import resolve_settings_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="photo_processor",
        description="Batch photo preparation core",
    )
    parser.add_argument("--source", required=True, help="Source folder with images")
    parser.add_argument("--output", help="Output folder, defaults to <source>/processed")
    parser.add_argument("--preset", choices=get_preset_ids())
    parser.add_argument("--width", type=float)
    parser.add_argument("--height", type=float)
    parser.add_argument("--units", choices=[unit.value for unit in Units])
    parser.add_argument("--dpi", type=int)
    parser.add_argument(
        "--resize-mode",
        choices=[mode.value for mode in ResizeMode],
    )
    parser.add_argument("--max-file-size-mb", type=float)
    parser.add_argument("--suffix", default="_processed")
    parser.add_argument(
        "--conflict-strategy",
        choices=[strategy.value for strategy in ConflictStrategy],
        default=ConflictStrategy.ADD_COUNTER.value,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--upload-provider",
        choices=[provider.value for provider in CloudProvider],
        help="Cloud provider for post-processing upload",
    )
    parser.add_argument("--upload-remote-folder", help="Remote folder identifier or path for the selected provider")
    parser.add_argument(
        "--upload-create-share-link",
        action="store_true",
        default=None,
        help="Create a shareable link after upload when the provider supports it",
    )
    parser.add_argument(
        "--upload-delete-local-after-upload",
        action="store_true",
        default=None,
        help="Delete the local processed file after a successful upload",
    )
    parser.add_argument(
        "--upload-overwrite-remote",
        action="store_true",
        default=None,
        help="Overwrite an existing remote file with the same name when supported",
    )
    return parser


def run_cli() -> int:
    load_cloud_oauth_env()
    storage = JsonSettingsStorage(resolve_settings_path())
    args = build_parser().parse_args()
    saved_snapshot = storage.load()
    settings = build_settings_from_args(args, saved_snapshot=saved_snapshot)
    execution = ProcessingController(cloud_uploader_factory=build_cloud_uploader).run(
        settings,
        dry_run=args.dry_run,
    )
    storage.save(build_snapshot_from_settings(settings, args.preset))
    report = execution.report
    for line in report.summary_lines:
        print(line)

    for message in execution.result.messages:
        print(message)
    for item in execution.result.items:
        for warning in item.warnings:
            print(f"WARNING {item.source_path}: {warning}")

    return 0 if report.error_files == 0 and report.upload_error_files == 0 else 1
