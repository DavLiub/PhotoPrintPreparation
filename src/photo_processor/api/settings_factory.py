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
from photo_processor.core.cloud_upload import CloudProvider, CloudUploadSettings
from photo_processor.core.output_policy import ConflictStrategy, OutputFormat, OutputPolicy
from photo_processor.core.settings import CropAnchor, ProcessingSettings, ResizeMode, SUPPORTED_INPUT_FORMATS, Units
from photo_processor.core.settings_snapshot import SettingsSnapshot


def _parse_resize_mode(value: str | None) -> ResizeMode:
    if value is None:
        return ResizeMode.CONTAIN
    try:
        return ResizeMode(value)
    except ValueError:
        return ResizeMode.CONTAIN


def _parse_crop_anchor(value: str | None) -> CropAnchor:
    if value is None:
        return CropAnchor.TOP_LEFT
    try:
        return CropAnchor(value)
    except ValueError:
        return CropAnchor.TOP_LEFT


def _parse_cloud_provider(value: str | None) -> CloudProvider | None:
    if value is None:
        return None
    try:
        return CloudProvider(value)
    except ValueError:
        return None


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
    auto_rotate = (
        preset.auto_rotate
        if preset
        else (snapshot.auto_rotate if snapshot.auto_rotate is not None else True)
    )
    resize_mode = (
        _parse_resize_mode(args.resize_mode)
        if args.resize_mode is not None
        else (
            preset.resize_mode
            if preset
            else _parse_resize_mode(snapshot.resize_mode)
        )
    )
    crop_anchor = _parse_crop_anchor(snapshot.crop_anchor)
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
    filename_suffix = args.suffix if args.suffix is not None else (snapshot.filename_suffix or "_processed")
    conflict_strategy = ConflictStrategy(args.conflict_strategy) if args.conflict_strategy is not None else (
        ConflictStrategy(snapshot.conflict_strategy)
        if snapshot.conflict_strategy is not None
        else ConflictStrategy.ADD_COUNTER
    )
    source_formats = snapshot.source_formats or SUPPORTED_INPUT_FORMATS
    output_format = OutputFormat(snapshot.output_format) if snapshot.output_format is not None else OutputFormat.JPEG
    cli_provider = getattr(args, "upload_provider", None)
    cloud_provider = _parse_cloud_provider(cli_provider if cli_provider is not None else snapshot.cloud_provider)
    cloud_upload_enabled = (
        cli_provider is not None
        if cli_provider is not None
        else (snapshot.cloud_upload_enabled if snapshot.cloud_upload_enabled is not None else False)
    )
    upload_remote_folder = getattr(args, "upload_remote_folder", None)
    upload_create_share_link = getattr(args, "upload_create_share_link", None)
    upload_delete_local_after_upload = getattr(args, "upload_delete_local_after_upload", None)
    upload_overwrite_remote = getattr(args, "upload_overwrite_remote", None)

    return ProcessingSettings(
        source_folder=source_folder,
        output_folder=output_folder,
        width=width,
        height=height,
        units=units,
        dpi=dpi,
        resize_mode=resize_mode,
        crop_anchor=crop_anchor,
        allow_both_orientations=allow_both_orientations,
        auto_rotate=auto_rotate,
        max_file_size_mb=max_file_size_mb,
        source_formats=tuple(source_formats),
        cloud_upload=CloudUploadSettings(
            enabled=cloud_upload_enabled,
            provider=cloud_provider,
            connection_id=snapshot.cloud_connection_id,
            account_email=snapshot.cloud_account_email,
            remote_folder=(
                upload_remote_folder
                if upload_remote_folder is not None
                else snapshot.cloud_remote_folder
            ),
            create_share_link=(
                upload_create_share_link
                if upload_create_share_link is not None
                else (snapshot.cloud_create_share_link if snapshot.cloud_create_share_link is not None else False)
            ),
            delete_local_after_upload=(
                upload_delete_local_after_upload
                if upload_delete_local_after_upload is not None
                else (
                    snapshot.cloud_delete_local_after_upload
                    if snapshot.cloud_delete_local_after_upload is not None
                    else False
                )
            ),
            overwrite_remote=(
                upload_overwrite_remote
                if upload_overwrite_remote is not None
                else (snapshot.cloud_overwrite_remote if snapshot.cloud_overwrite_remote is not None else False)
            ),
        ),
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
        auto_rotate=settings.auto_rotate,
        resize_mode=settings.resize_mode.value,
        crop_anchor=settings.crop_anchor.value,
        max_file_size_mb=settings.max_file_size_mb,
        filename_suffix=settings.output_policy.filename_suffix,
        conflict_strategy=settings.output_policy.conflict_strategy.value,
        source_formats=settings.source_formats,
        output_format=settings.output_policy.output_format.value,
        cloud_upload_enabled=settings.cloud_upload.enabled,
        cloud_provider=settings.cloud_upload.provider.value if settings.cloud_upload.provider is not None else None,
        cloud_connection_id=settings.cloud_upload.connection_id,
        cloud_account_email=settings.cloud_upload.account_email,
        cloud_remote_folder=settings.cloud_upload.remote_folder,
        cloud_create_share_link=settings.cloud_upload.create_share_link,
        cloud_delete_local_after_upload=settings.cloud_upload.delete_local_after_upload,
        cloud_overwrite_remote=settings.cloud_upload.overwrite_remote,
    )
