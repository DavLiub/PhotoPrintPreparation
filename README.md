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
- post-processing cloud export backend with initial `Google Drive` support in the CLI and GUI flows

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
python -m photo_processor --source "C:\Photos" --upload-provider google_drive --upload-remote-folder "<drive-folder-id>"
python -m photo_processor.api.gui_app
```

The CLI and GUI now persist last-used settings in `%ProgramData%\PhotoPrintPreparation\settings.json`.

The target authentication model for `Google Drive` is browser-based OAuth:

1. open the browser for Google sign-in
2. receive an authorization code on a local callback
3. exchange it for a refresh token
4. save that refresh token in a Windows-protected secret store

The `Google Drive` browser flow is now available from the GUI `Setup` tab through `Connect Google Drive`.

For local release builds, keep the real app-level OAuth settings in a local non-committed module:

```text
src/photo_processor/config/cloud_oauth_embedded.py
```

Start by copying:

```text
src/photo_processor/config/cloud_oauth_embedded.py.template
```

to:

```text
src/photo_processor/config/cloud_oauth_embedded.py
```

and fill in the real Google OAuth client values for this application.

`config/cloud_oauth.env` remains available only as a development override.

At runtime, the uploader resolves credentials in this order:

1. a saved encrypted local secret for the configured cloud connection
2. embedded app-level credentials from `src/photo_processor/config/cloud_oauth_embedded.py`
3. environment-variable fallback for CLI or development use

Embedded local build-time OAuth config:

```python
GOOGLE_DRIVE_CLIENT_ID = "..."
GOOGLE_DRIVE_CLIENT_SECRET = "..."
```

Optional development `.env` override:

```env
PHOTO_PROCESSOR_GDRIVE_CLIENT_ID=...
PHOTO_PROCESSOR_GDRIVE_CLIENT_SECRET=...
```

Current environment-variable fallback for CLI and development use:

```powershell
$env:PHOTO_PROCESSOR_GDRIVE_CLIENT_ID = "..."
$env:PHOTO_PROCESSOR_GDRIVE_REFRESH_TOKEN = "..."
$env:PHOTO_PROCESSOR_GDRIVE_CLIENT_SECRET = "..."  # required when the Google OAuth client expects a secret
```

The current GUI is organized around four tabs:

- `Setup` for source and output folders plus preset selection
- `Setup` also includes cloud export configuration, provider cards for `Google Drive` and `Dropbox`, a connection-status indicator, connected-account details, remote-folder input, and `Google Drive` connect/disconnect actions
- `Setup` also includes input-format checkboxes and output extension selection
- `Processing` for resize, crop anchor, auto-rotate, and output constraints
- `Manual` for one-file visual preview with alternate fit modes, output-name preview, and save-current behavior
- `Report` for user-facing processing summary

The GUI can now browse folders, save current settings, run full processing, and open the output folder.
It also includes a searchable Help dialog with parameter descriptions and external reference links such as DPI on Wikipedia.
The `About` dialog now shows the product name, version, license model, and copyright.

## Versioning Rule

When the application version changes, update these files together:

- `pyproject.toml`
- `src/photo_processor/config/app_info.py`

Use a simple semantic progression:

- patch: bug fixes and packaging-only fixes
- minor: new user-visible features or settings
- major: breaking workflow or compatibility changes

Do not ship a release where `pyproject.toml` and `APP_VERSION` disagree.

## Layout

- `src/` source container for the Python project
- `src/photo_processor/` root application package
- `src/photo_processor/api`, `app`, `core`, `infra`, `bootstrap`, `config`, `gui` application packages
- `tests/` unit tests for core rules
- `build.bat` local install and test helper
- `run.bat` local CLI launcher
- `run_gui.bat` local GUI launcher

## Build Portable Windows EXE

The project does not yet ship with an automated packaging script, but you can build a portable GUI bundle with `PyInstaller`.

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pyinstaller
```

If you want to run package modules directly before packaging, add `src` to `PYTHONPATH` in the current shell:

```powershell
$env:PYTHONPATH = "$PWD\src"
```

2. Build a one-folder portable GUI package:

Run the build from the repository root. The tracked spec file generates the embedded OAuth module during packaging, includes it in the bundle, and fails early if the Google OAuth client values are missing.

Optional pre-check:

```powershell
.\.venv\Scripts\python.exe -m photo_processor.bootstrap.build_embedded_oauth
Get-Content .\src\photo_processor\config\cloud_oauth_embedded.py
```

```powershell
pyinstaller --noconfirm --clean PhotoPrintPreparation.spec
```

If `pyinstaller` is not available in `PATH`, use the interpreter from `.venv` directly:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean PhotoPrintPreparation.spec
```

The tracked `PhotoPrintPreparation.spec` automatically adds the matching `python312.dll` from the Python environment when that file exists.

3. The portable build will appear under:

```text
dist\PhotoPrintPreparation\
```

Run:

```text
dist\PhotoPrintPreparation\PhotoPrintPreparation.exe
```

Before building a portable release, provide local Google OAuth credentials in one of these ways:

1. create the local non-committed file:

```text
src\photo_processor\config\cloud_oauth_embedded.py
```

using the tracked template:

```text
src\photo_processor\config\cloud_oauth_embedded.py.template
```

2. or place the same values in:

```text
config\cloud_oauth.env
```

The build spec uses those local credentials to generate `cloud_oauth_embedded.py`, includes that module in the packaged binary, and stops the build if the credentials are missing.

The optional `cloud_oauth.env` sidecar remains supported for development overrides, but it is no longer the recommended release mechanism.

Notes:

- `one-folder` packaging is the recommended portable format for this project.
- the built `.exe` has the same architecture as the Python used for packaging:
  - `64-bit Python` -> `64-bit EXE`
  - `32-bit Python` -> `32-bit EXE`
- settings are still stored in `%ProgramData%\PhotoPrintPreparation\settings.json`
- if you later add a Windows `.ico` asset, pass it to `PyInstaller` with `--icon path\to\app.ico`
