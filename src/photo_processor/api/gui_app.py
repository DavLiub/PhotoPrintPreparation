from __future__ import annotations

import sys
import ctypes

from photo_processor.app.controllers.processing_controller import ProcessingController
from photo_processor.app.controllers.settings_controller import SettingsController
from photo_processor.app.i18n.translator import Translator
from photo_processor.gui.main_window import MainWindow
from photo_processor.gui.icon_provider import app_icon_path, build_icon
from photo_processor.infra.settings_storage.json_settings_storage import JsonSettingsStorage
from photo_processor.infra.settings_storage.storage_paths import resolve_settings_path


def run_gui() -> int:
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise RuntimeError("PySide6 is required to run the GUI.") from exc

    if sys.platform.startswith("win"):
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PhotoPrintPreparation.App")
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setWindowIcon(build_icon(app_icon_path()))
    translator = Translator(language="en")
    storage = JsonSettingsStorage(resolve_settings_path())
    settings_controller = SettingsController(storage)
    processing_controller = ProcessingController()
    window = MainWindow(translator, settings_controller, processing_controller)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run_gui())
