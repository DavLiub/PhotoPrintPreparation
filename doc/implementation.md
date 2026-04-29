# Implementation Notes

## Implemented now

The current repository implements the first technical slice of the product:

- CLI argument parsing in `src/photo_processor/main.py`
- processing settings in `src/photo_processor/core/settings.py`
- centimeter-to-pixel conversion in `src/photo_processor/core/units.py`
- resize plan math in `src/photo_processor/core/resize_rules.py`
- orientation choice logic in `src/photo_processor/core/orientation.py`
- source scanning and output naming in `src/photo_processor/infra/filesystem/`
- one-image processing in `src/photo_processor/infra/imaging/`
- batch orchestration and result aggregation in `src/photo_processor/app/use_cases/batch_processing.py`
- per-file structured results in `src/photo_processor/core/single_image_result.py`
- unit and integration tests for math, paths, planning, and one-image processing in `tests/`

## Planned next

The code still has planned gaps:

- GUI, preview, settings persistence, and packaging are not implemented yet
- advanced output policies and presets are not implemented yet

## Convergence with product specification

The product specification in `source doc/PhotoProject_expanded.docx` expects:

- a complete one-image processing pipeline
- JPEG output under a size limit
- multiple frame fit modes
- orientation-aware target frame selection
- later a GUI and portable Windows build

The repository is aligned with the recommended implementation order from the specification:

1. project skeleton
2. settings model
3. unit conversion
4. resize calculation
5. tests for math
6. real image processing
7. batch processing completion
8. GUI and packaging

## Documentation maintenance rule

Whenever a planned module becomes real code, move it from `Planned next` to `Implemented now`.
