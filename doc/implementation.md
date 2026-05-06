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
- JSON settings persistence in `src/photo_processor/infra/settings_storage/`, with runtime storage resolved to `%ProgramData%\PhotoPrintPreparation\settings.json` on Windows
- desktop GUI scaffold in `src/photo_processor/gui/` and `src/photo_processor/api/gui_app.py`
- combined `Setup` tab for source/output configuration, simplified menu, and stronger action-button styling
- `Manual` tab for one-file preview, per-file fit-mode switching, output-name preview, and save-current output
- input-format filtering and output-extension selection in the GUI settings model
- explicit `auto_rotate` and `crop_anchor` controls in GUI processing settings and settings persistence
- real GUI actions for folder browsing, full batch start, output-folder opening, and report rendering
- searchable GUI Help dialog with parameter descriptions and external reference links
- translation layer in `src/photo_processor/app/i18n/` and `src/photo_processor/config/translations.py` with `en`, `ru`, and `he`
- quality warnings for source images smaller than the target frame
- unit and integration tests for math, paths, planning, and one-image processing in `tests/`

## Planned next

The code still has planned gaps:

- GUI packaging and richer pre-processing preview are not implemented yet
- advanced output policies beyond current strategies are not implemented yet

## Planned post-processing roadmap

The next major extension under discussion is post-processing for cloud export of already processed photos.

This is not implemented yet. The intended direction is:

1. keep local image generation as the primary processing outcome
2. add a separate post-processing stage after local files are written
3. upload only successfully generated output files
4. report upload success and upload failure independently from local processing success

### Target architecture

The cloud export feature should follow the existing layer split:

- `core/` for provider-neutral settings and upload result models
- `app/` for post-processing orchestration and workflow decisions
- `infra/` for concrete cloud adapters and credential storage
- `gui/` and later CLI extensions for user-facing configuration and execution

The upload flow should not be embedded inside `infra/imaging/image_processor.py`.
Image generation and cloud publication are separate responsibilities and should remain separate modules.

### Planned implementation stages

1. Extend domain models:
   - add provider-neutral cloud upload settings
   - add upload status and upload result models
   - extend per-file processing results with remote upload metadata
2. Add an application-level post-processing use case:
   - accept `BatchProcessingResult`
   - filter successful local outputs
   - upload those outputs through an uploader port
   - enrich the final result and report without hiding partial failures
3. Integrate post-processing into the main controller flow:
   - run local batch processing first
   - run upload only when enabled
   - keep local processing success separate from remote publication success
4. Add settings persistence for cloud export:
   - keep normal UI settings in the existing settings snapshot
   - store secrets and tokens separately from general settings when practical
5. Add minimal GUI support:
   - enable or disable cloud upload
   - choose provider
   - configure remote folder
   - test connection or credentials
6. Extend reporting:
   - count uploaded files
   - count upload failures
   - store remote path, remote file id, or shareable link when available

### Provider order

The planned provider sequence is:

1. `Google Drive`
2. `Dropbox`

This order matters because `Google Drive` is the first target and should shape the initial uploader contract, but the contract must remain provider-neutral enough that `Dropbox` can be added without changing application-layer workflow.

### Google Drive first-phase scope

The first `Google Drive` slice should stay intentionally narrow:

- upload processed files into a configured target folder
- use stored credentials or tokens instead of a full in-app OAuth wizard
- return enough metadata for reporting, such as remote id and link
- leave local files in place after successful upload

The first phase should not depend on deleting local files, background sync, or advanced folder browsing UX.

### Dropbox follow-up scope

After the common post-processing contract is stable, add a `Dropbox` adapter using the same application-level workflow:

- reuse post-processing orchestration
- reuse result reporting
- keep provider-specific API details inside `infra/cloud/`

### Testing plan

The cloud export roadmap requires tests at multiple levels:

- unit tests for the post-processing use case with fake uploaders
- settings serialization tests for new cloud-related models
- controller tests for combined local processing and upload flow
- optional opt-in integration tests for real provider adapters with external credentials

### Current documentation gap

The product specification in `source doc/PhotoProject_expanded.docx` remains the functional source of truth for image processing behavior.
The cloud export direction described here is currently a repository-level technical roadmap and should be reflected in the source specification when the feature scope is accepted as part of the product behavior.

## Convergence with product specification

The product specification in `source doc/PhotoProject_expanded.docx` expects:

- a complete one-image processing pipeline
- JPEG output under a size limit
- multiple frame fit modes for contain, fit by width, and fit by height
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
