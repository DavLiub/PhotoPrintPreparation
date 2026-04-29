# Data Model

## Current structures

### ProcessingSettings

Defined in `src/photo_processor/core/settings.py`.

Purpose:

- capture source and output folders
- define target frame dimensions
- define units and DPI
- define resize policy and orientation behavior
- define output suffix and file-size limit

Important fields:

- `source_folder: Path`
- `output_folder: Path`
- `width: float`
- `height: float`
- `units: Units`
- `dpi: int`
- `resize_mode: ResizeMode`
- `allow_both_orientations: bool`
- `auto_rotate: bool`
- `max_file_size_mb: float`
- `filename_suffix: str`

### ImageTask

Defined in `src/photo_processor/core/image_task.py`.

Purpose:

- bind one source file to one resolved output file

### BatchProcessingResult

Defined in `src/photo_processor/core/processing_result.py`.

Purpose:

- aggregate processing counters
- keep per-file processing items
- expose human-readable log messages for CLI and later GUI

### SingleImageResult

Defined in `src/photo_processor/core/single_image_result.py`.

Purpose:

- describe one processed file or one failed file
- carry warnings, output metadata, and future GUI-facing details

### ImageInfo

Defined in `src/photo_processor/core/image_info.py`.

Purpose:

- describe image width, height, mode, and format
- normalize source and output metadata into one reusable structure

## Intended evolution

The current core model set is acceptable for a small prototype, but the target architecture should separate:

- core value objects such as frame size, resize mode, and orientation policy
- app request/response DTOs for batch execution
- infra metadata such as filesystem scan results and saved-file stats

## Recommended next model additions

- `FrameSize` value object with unit-aware conversion
- `OutputPolicy` for suffix, format, and overwrite behavior
- `ProcessingReport` for batch-level summary plus per-file details
