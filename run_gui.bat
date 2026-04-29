@echo off
set PYTHONPATH=%CD%\src
.\.venv\Scripts\python.exe -m photo_processor.api.gui_app
