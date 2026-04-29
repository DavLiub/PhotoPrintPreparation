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
- desktop GUI with `en/ru/he` localization support

Preview and richer live processing behavior are still incomplete, but the GUI now supports folder selection, full batch start, and report display.

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

The CLI and GUI now persist last-used settings in `%ProgramData%\PhotoPrintPreparation\settings.json`.

The current GUI is organized around three tabs:

- `Setup` for source and output folders plus preset selection
- `Setup` also includes input-format checkboxes and output extension selection
- `Processing` for resize and output constraints
- `Report` for user-facing processing summary

The GUI can now browse folders, save current settings, run full processing, and open the output folder.
It also includes a searchable Help dialog with parameter descriptions and external reference links such as DPI on Wikipedia.
The `About` dialog now shows the product name, version, license model, and copyright.

## Layout

- `src/` source container for the Python project
- `src/photo_processor/` root application package
- `src/photo_processor/api`, `app`, `core`, `infra`, `bootstrap`, `config`, `gui` application packages
- `tests/` unit tests for core rules
- `build.bat` local install and test helper
- `run.bat` local CLI launcher
- `run_gui.bat` local GUI launcher
