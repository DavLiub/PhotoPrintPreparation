from __future__ import annotations

import argparse
from pathlib import Path

from photo_processor.app.use_cases.batch_processing import BatchProcessingUseCase
from photo_processor.core.settings import ProcessingSettings, ResizeMode, Units


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="photo_processor",
        description="Batch photo preparation core",
    )
    parser.add_argument("--source", required=True, help="Source folder with images")
    parser.add_argument("--output", help="Output folder, defaults to <source>/processed")
    parser.add_argument("--width", type=float, default=1500)
    parser.add_argument("--height", type=float, default=1000)
    parser.add_argument("--units", choices=[unit.value for unit in Units], default=Units.PIXELS.value)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument(
        "--resize-mode",
        choices=[mode.value for mode in ResizeMode],
        default=ResizeMode.CONTAIN.value,
    )
    parser.add_argument("--max-file-size-mb", type=float, default=2.0)
    parser.add_argument("--suffix", default="_processed")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def run_cli() -> int:
    args = build_parser().parse_args()
    source_folder = Path(args.source).expanduser().resolve()
    output_folder = Path(args.output).expanduser().resolve() if args.output else source_folder / "processed"

    settings = ProcessingSettings(
        source_folder=source_folder,
        output_folder=output_folder,
        width=args.width,
        height=args.height,
        units=Units(args.units),
        dpi=args.dpi,
        resize_mode=ResizeMode(args.resize_mode),
        max_file_size_mb=args.max_file_size_mb,
        filename_suffix=args.suffix,
    )

    result = BatchProcessingUseCase(settings).run(dry_run=args.dry_run)
    print(f"Found files: {result.found_files}")
    print(f"Processed: {result.processed_files}")
    print(f"Skipped: {result.skipped_files}")
    print(f"Errors: {result.error_files}")

    for message in result.messages:
        print(message)

    return 0 if result.error_files == 0 else 1
