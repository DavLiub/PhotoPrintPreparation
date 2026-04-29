from __future__ import annotations

import argparse

from photo_processor.api.settings_factory import build_settings_from_args
from photo_processor.app.use_cases.batch_processing import BatchProcessingUseCase
from photo_processor.config.presets import get_preset_ids
from photo_processor.core.output_policy import ConflictStrategy
from photo_processor.core.settings import ResizeMode, Units


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
    args = build_parser().parse_args()
    settings = build_settings_from_args(args)
    result = BatchProcessingUseCase(settings).run(dry_run=args.dry_run)
    print(f"Found files: {result.found_files}")
    print(f"Processed: {result.processed_files}")
    print(f"Skipped: {result.skipped_files}")
    print(f"Errors: {result.error_files}")

    for message in result.messages:
        print(message)
    for item in result.items:
        for warning in item.warnings:
            print(f"WARNING {item.source_path}: {warning}")

    return 0 if result.error_files == 0 else 1
