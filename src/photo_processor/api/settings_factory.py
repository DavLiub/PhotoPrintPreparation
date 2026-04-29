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
from photo_processor.core.settings import ProcessingSettings, ResizeMode, SUPPORTED_INPUT_FORMATS, Units
from photo_processor.core.settings_snapshot import SettingsSnapshot


def build_settings_from_args(
    args: Namespace,
    saved_snapshot: SettingsSnapshot | None = None,
) -> ProcessingSettings:
    source_folder = Path(args.source).expanduser().resolve()
    output_folder = Path(args.output).expanduser().resolve() if args.output else source_folder / "processed"

    preset = get_preset(args.preset) if args.preset else None
    snapshot = saved_snapshot or SettingsSnapshot()

    width = args.width if args.width is not None else (
        preset.width if preset else (snapshot.width if snapshot.width is not None else DEFAULT_WIDTH)
    )
    height = args.height if args.height is not None else (
        preset.height if preset else (snapshot.height if snapshot.height is not None else DEFAULT_HEIGHT)
    )
    units = Units(args.units) if args.units is not None else (
        preset.units if preset else (Units(snapshot.units) if snapshot.units is not None else Units.PIXELS)
    )
    dpi = args.dpi if args.dpi is not None else (
        preset.dpi if preset else (snapshot.dpi if snapshot.dpi is not None else DEFAULT_DPI)
    )
    resize_mode = (
        ResizeMode(args.resize_mode)
        if args.resize_mode is not None
        else (
            preset.resize_mode
            if preset
            else (ResizeMode(snapshot.resize_mode) if snapshot.resize_mode is not None else ResizeMode.CONTAIN)
        )
    )
    max_file_size_mb = (
        args.max_file_size_mb
        if args.max_file_size_mb is not None
        else (
            preset.max_file_size_mb
            if preset
            else (
                snapshot.max_file_size_mb
                if snapshot.max_file_size_mb is not None
                else DEFAULT_MAX_FILE_SIZE_MB
            )
        )
    )
    allow_both_orientations = preset.allow_both_orientations if preset else True
    auto_rotate = preset.auto_rotate if preset else True
    filename_suffix = args.suffix if args.suffix is not None else (snapshot.filename_suffix or "_processed")
    conflict_strategy = ConflictStrategy(args.conflict_strategy) if args.conflict_strategy is not None else (
        ConflictStrategy(snapshot.conflict_strategy)
        if snapshot.conflict_strategy is not None
        else ConflictStrategy.ADD_COUNTER
    )
    source_formats = snapshot.source_formats or SUPPORTED_INPUT_FORMATS
    output_format = OutputFormat(snapshot.output_format) if snapshot.output_format is not None else OutputFormat.JPEG

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
        source_formats=tuple(source_formats),
        output_policy=OutputPolicy(
            filename_suffix=filename_suffix,
            output_format=output_format,
            conflict_strategy=conflict_strategy,
        ),
    )


def build_snapshot_from_settings(settings: ProcessingSettings, preset_id: str | None) -> SettingsSnapshot:
    return SettingsSnapshot(
        preset_id=preset_id,
        source_folder=str(settings.source_folder),
        output_folder=str(settings.output_folder),
        width=settings.width,
        height=settings.height,
        units=settings.units.value,
        dpi=settings.dpi,
        resize_mode=settings.resize_mode.value,
        max_file_size_mb=settings.max_file_size_mb,
        filename_suffix=settings.output_policy.filename_suffix,
        conflict_strategy=settings.output_policy.conflict_strategy.value,
        source_formats=settings.source_formats,
        output_format=settings.output_policy.output_format.value,
    )
