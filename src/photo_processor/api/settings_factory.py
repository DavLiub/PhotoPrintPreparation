from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from photo_processor.config.defaults import (
    DEFAULT_DPI,
    DEFAULT_HEIGHT,
    DEFAULT_MAX_FILE_SIZE_MB,
    DEFAULT_WIDTH,
)
from photo_processor.config.presets import get_preset
from photo_processor.core.output_policy import ConflictStrategy, OutputFormat, OutputPolicy
from photo_processor.core.settings import ProcessingSettings, ResizeMode, Units


def build_settings_from_args(args: Namespace) -> ProcessingSettings:
    source_folder = Path(args.source).expanduser().resolve()
    output_folder = Path(args.output).expanduser().resolve() if args.output else source_folder / "processed"

    preset = get_preset(args.preset) if args.preset else None

    width = args.width if args.width is not None else (preset.width if preset else DEFAULT_WIDTH)
    height = args.height if args.height is not None else (preset.height if preset else DEFAULT_HEIGHT)
    units = Units(args.units) if args.units is not None else (preset.units if preset else Units.PIXELS)
    dpi = args.dpi if args.dpi is not None else (preset.dpi if preset else DEFAULT_DPI)
    resize_mode = (
        ResizeMode(args.resize_mode)
        if args.resize_mode is not None
        else (preset.resize_mode if preset else ResizeMode.CONTAIN)
    )
    max_file_size_mb = (
        args.max_file_size_mb
        if args.max_file_size_mb is not None
        else (preset.max_file_size_mb if preset else DEFAULT_MAX_FILE_SIZE_MB)
    )
    allow_both_orientations = preset.allow_both_orientations if preset else True
    auto_rotate = preset.auto_rotate if preset else True

    return ProcessingSettings(
        source_folder=source_folder,
        output_folder=output_folder,
        width=width,
        height=height,
        units=units,
        dpi=dpi,
        resize_mode=resize_mode,
        allow_both_orientations=allow_both_orientations,
        auto_rotate=auto_rotate,
        max_file_size_mb=max_file_size_mb,
        output_policy=OutputPolicy(
            filename_suffix=args.suffix,
            output_format=OutputFormat.JPEG,
            conflict_strategy=ConflictStrategy(args.conflict_strategy),
        ),
    )
