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
- user-facing report building in `src/photo_processor/app/reporting/report_builder.py`
- per-file structured results in `src/photo_processor/core/single_image_result.py`
- presentation summary model in `src/photo_processor/core/processing_report.py`
- image metadata normalization in `src/photo_processor/core/image_info.py`
- output behavior modeling in `src/photo_processor/core/output_policy.py`
- preset registry and preset-aware CLI settings resolution in `src/photo_processor/config/presets.py` and `src/photo_processor/api/settings_factory.py`
- JSON settings persistence in `src/photo_processor/infra/settings_storage/json_settings_storage.py`
- desktop GUI scaffold in `src/photo_processor/gui/` and `src/photo_processor/api/gui_app.py`
- English-first translation layer in `src/photo_processor/app/i18n/` and `src/photo_processor/config/translations.py`
- quality warnings for source images smaller than the target frame
- unit and integration tests for math, paths, planning, and one-image processing in `tests/`

## Planned next

The code still has planned gaps:

- live GUI processing workflow, preview, and packaging are not implemented yet
- advanced output policies beyond current strategies are not implemented yet

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
