from __future__ import annotations

import sys
from pathlib import Path

from photo_processor.app.controllers.settings_controller import SettingsController
from photo_processor.app.i18n.translator import Translator
from photo_processor.gui.main_window import MainWindow
from photo_processor.infra.settings_storage.json_settings_storage import JsonSettingsStorage


def run_gui() -> int:
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise RuntimeError("PySide6 is required to run the GUI.") from exc

    app = QApplication(sys.argv)
    translator = Translator(language="en")
    storage = JsonSettingsStorage(Path("config/settings.json"))
    controller = SettingsController(storage)
    window = MainWindow(translator, controller)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run_gui())
