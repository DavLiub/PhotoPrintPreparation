# Implementation Notes

## Implemented now

The current repository implements the first technical slice of the product:

- CLI argument parsing in `src/photo_processor/main.py`
- processing settings in `src/photo_processor/core/settings.py`
- centimeter-to-pixel conversion in `src/photo_processor/core/units.py`
- resize plan math in `src/photo_processor/core/resize_rules.py`
- orientation choice logic in `src/photo_processor/core/orientation.py`
- source scanning and output naming in `src/photo_processor/services/`
- batch orchestration and result aggregation in `src/photo_processor/core/batch_processor.py`
- unit tests for the math and path rules in `tests/`

## Not implemented yet

The code intentionally stops before real image transformation:

- `core/image_processor.py` is a placeholder
- EXIF orientation is not applied yet
- Pillow is not used yet
- JPEG file-size optimization is not implemented yet
- GUI, preview, settings persistence, and packaging are not implemented yet

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

Whenever a planned module becomes real code, update this file to move it from `Not implemented yet` to `Implemented now`.
