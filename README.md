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
- batch report structure

Pixel-level image processing and GUI are the next stages.

## Quick start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python -m photo_processor --source "C:\Photos" --dry-run
```

## Layout

- `src/` source container for the Python project
- `src/photo_processor/` root application package
- `src/photo_processor/api`, `app`, `core`, `infra`, `bootstrap`, `config` application layers
- `tests/` unit tests for core rules
- `build.bat` placeholder for packaging flow
- `run.bat` local CLI launcher
