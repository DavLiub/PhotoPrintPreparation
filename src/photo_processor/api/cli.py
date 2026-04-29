from __future__ import annotations

import argparse
from pathlib import Path

from photo_processor.app.reporting.report_builder import build_processing_report
from photo_processor.api.settings_factory import build_settings_from_args, build_snapshot_from_settings
from photo_processor.app.use_cases.batch_processing import BatchProcessingUseCase
from photo_processor.config.presets import get_preset_ids
from photo_processor.core.output_policy import ConflictStrategy
from photo_processor.core.settings import ResizeMode, Units
from photo_processor.infra.settings_storage.json_settings_storage import JsonSettingsStorage


SETTINGS_PATH = Path("config/settings.json")


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
    return parser


def run_cli() -> int:
    storage = JsonSettingsStorage(SETTINGS_PATH)
    args = build_parser().parse_args()
    saved_snapshot = storage.load()
    settings = build_settings_from_args(args, saved_snapshot=saved_snapshot)
    result = BatchProcessingUseCase(settings).run(dry_run=args.dry_run)
    storage.save(build_snapshot_from_settings(settings, args.preset))
    report = build_processing_report(result)
    for line in report.summary_lines:
        print(line)

    for message in result.messages:
        print(message)
    for item in result.items:
        for warning in item.warnings:
            print(f"WARNING {item.source_path}: {warning}")

    return 0 if report.error_files == 0 else 1
