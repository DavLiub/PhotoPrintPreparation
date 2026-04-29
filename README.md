# Photo Print Preparation

Core-first Python project for batch preparation of photos for print and reports.

## Current scope

Version `0.1` focuses on the non-UI foundation:

- CLI entry point
- source folder scanning
- settings model
- unit conversion
- resize and orientation calculations
- output path generation
- one-image Pillow processing pipeline
- batch report structure
- preset-based processing scenarios
- desktop GUI scaffold with `en/ru/he` localization support

Preview and richer live processing behavior are the next stages.

## Quick start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python -m photo_processor --source "C:\Photos" --output "C:\Photos\processed"
python -m photo_processor --source "C:\Photos" --preset print_10x15
python -m photo_processor.api.gui_app
```

The CLI now persists last-used settings in `config/settings.json`.

The current GUI is organized around three tabs:

- `Setup` for source and output folders plus preset selection
- `Setup` also includes input-format checkboxes and output extension selection
- `Processing` for resize and output constraints
- `Report` for user-facing processing summary

## Layout

- `src/` source container for the Python project
- `src/photo_processor/` root application package
- `src/photo_processor/api`, `app`, `core`, `infra`, `bootstrap`, `config`, `gui` application packages
- `tests/` unit tests for core rules
- `build.bat` local install and test helper
- `run.bat` local CLI launcher
- `run_gui.bat` local GUI launcher
