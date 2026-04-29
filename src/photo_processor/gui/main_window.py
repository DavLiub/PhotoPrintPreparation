from __future__ import annotations

from pathlib import Path

from photo_processor.app.controllers.settings_controller import SettingsController
from photo_processor.app.i18n.translator import Translator
from photo_processor.config.presets import PRESETS
from photo_processor.core.output_policy import ConflictStrategy
from photo_processor.core.settings import ProcessingSettings, ResizeMode, Units
from photo_processor.gui.tabs.processing_tab import ProcessingTab
from photo_processor.gui.tabs.report_tab import ReportTab
from photo_processor.gui.tabs.setup_tab import SetupTab

try:
    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import (
        QHBoxLayout,
        QMainWindow,
        QMenu,
        QMenuBar,
        QMessageBox,
        QPushButton,
        QStatusBar,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )

    class MainWindow(QMainWindow):
        def __init__(self, translator: Translator, settings_controller: SettingsController) -> None:
            super().__init__()
            self.translator = translator
            self.settings_controller = settings_controller
            self._setup_ui()
            self._load_saved_snapshot()
            self._retranslate()

        def _setup_ui(self) -> None:
            self.setMinimumSize(980, 680)
            self._build_menu()
            self._build_central_widget()
            self.setStatusBar(QStatusBar(self))

        def _build_menu(self) -> None:
            menu_bar = QMenuBar(self)
            self.setMenuBar(menu_bar)
            self.language_menu = QMenu(menu_bar)
            self.help_menu = QMenu(menu_bar)
            self.help_action = QAction(self)
            self.help_action.triggered.connect(self._show_help)
            self.about_action = QAction(self)
            self.about_action.triggered.connect(self._show_about)
            self.lang_en_action = QAction(self)
            self.lang_en_action.triggered.connect(lambda: self._switch_language("en"))
            self.lang_ru_action = QAction(self)
            self.lang_ru_action.triggered.connect(lambda: self._switch_language("ru"))
            self.lang_he_action = QAction(self)
            self.lang_he_action.triggered.connect(lambda: self._switch_language("he"))
            menu_bar.addMenu(self.language_menu)
            menu_bar.addMenu(self.help_menu)
            self.language_menu.addAction(self.lang_en_action)
            self.language_menu.addAction(self.lang_ru_action)
            self.language_menu.addAction(self.lang_he_action)
            self.help_menu.addAction(self.help_action)
            self.help_menu.addAction(self.about_action)

        def _build_central_widget(self) -> None:
            root = QWidget(self)
            layout = QVBoxLayout(root)
            self.tabs = QTabWidget(root)
            self.setup_tab = SetupTab(self._apply_selected_preset, root)
            self.processing_tab = ProcessingTab(root)
            self.report_tab = ReportTab(root)
            self.tabs.addTab(self.setup_tab, "")
            self.tabs.addTab(self.processing_tab, "")
            self.tabs.addTab(self.report_tab, "")

            actions_row = QHBoxLayout()
            self.preview_button = QPushButton(root)
            self.start_button = QPushButton(root)
            self.open_output_button = QPushButton(root)
            self.save_settings_button = QPushButton(root)
            self.save_settings_button.clicked.connect(self._save_settings)
            self._style_action_buttons()
            actions_row.addWidget(self.preview_button)
            actions_row.addWidget(self.start_button)
            actions_row.addWidget(self.open_output_button)
            actions_row.addStretch(1)
            actions_row.addWidget(self.save_settings_button)

            layout.addWidget(self.tabs)
            layout.addLayout(actions_row)
            self.setCentralWidget(root)

        def _style_action_buttons(self) -> None:
            base_style = """
            QPushButton {
                min-height: 38px;
                padding: 6px 14px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                border: 1px solid #cbd5e1;
            }
            """
            neutral_style = (
                base_style
                + "QPushButton { background-color: #f8fafc; color: #0f172a; } "
                + "QPushButton:hover { background-color: #e2e8f0; }"
            )
            primary_style = (
                base_style
                + "QPushButton { background-color: #2563eb; color: #ffffff; border: none; } "
                + "QPushButton:hover { background-color: #1d4ed8; }"
            )
            self.preview_button.setStyleSheet(neutral_style)
            self.open_output_button.setStyleSheet(neutral_style)
            self.save_settings_button.setStyleSheet(neutral_style)
            self.start_button.setStyleSheet(primary_style)

        def _build_settings(self) -> ProcessingSettings:
            source_folder = Path(self.setup_tab.source_path_edit.text() or ".").resolve()
            output_folder = Path(self.setup_tab.output_path_edit.text() or (source_folder / "processed")).resolve()
            from photo_processor.core.output_policy import OutputFormat, OutputPolicy

            return ProcessingSettings(
                source_folder=source_folder,
                output_folder=output_folder,
                width=float(self.processing_tab.width_spin.value()),
                height=float(self.processing_tab.height_spin.value()),
                units=Units(self.processing_tab.units_combo.currentData()),
                dpi=int(self.processing_tab.dpi_spin.value()),
                resize_mode=ResizeMode(self.processing_tab.resize_mode_combo.currentData()),
                max_file_size_mb=float(self.processing_tab.max_file_size_spin.value()),
                source_formats=self.setup_tab.selected_source_formats(),
                output_policy=OutputPolicy(
                    filename_suffix=self.setup_tab.suffix_edit.text(),
                    output_format=self.setup_tab.selected_output_format(),
                    conflict_strategy=ConflictStrategy(self.setup_tab.conflict_combo.currentData()),
                ),
            )

        def _load_saved_snapshot(self) -> None:
            snapshot = self.settings_controller.load_snapshot()
            if snapshot is None:
                self._apply_defaults()
                return
            self.setup_tab.source_path_edit.setText(snapshot.source_folder or "")
            self.setup_tab.output_path_edit.setText(snapshot.output_folder or "")
            self.processing_tab.width_spin.setValue(snapshot.width or 1500)
            self.processing_tab.height_spin.setValue(snapshot.height or 1000)
            self.processing_tab.dpi_spin.setValue(snapshot.dpi or 300)
            self.processing_tab.max_file_size_spin.setValue(snapshot.max_file_size_mb or 2.0)
            self.setup_tab.suffix_edit.setText(snapshot.filename_suffix or "_processed")
            self.setup_tab.set_source_formats(snapshot.source_formats)
            self.setup_tab.set_output_format(snapshot.output_format)
            self._set_combo_data(self.processing_tab.units_combo, snapshot.units or Units.PIXELS.value)
            self._set_combo_data(self.processing_tab.resize_mode_combo, snapshot.resize_mode or ResizeMode.CONTAIN.value)
            self._set_combo_data(self.setup_tab.conflict_combo, snapshot.conflict_strategy or ConflictStrategy.ADD_COUNTER.value)
            if snapshot.preset_id:
                self._set_combo_data(self.setup_tab.preset_combo, snapshot.preset_id)

        def _apply_defaults(self) -> None:
            self.processing_tab.width_spin.setValue(1500)
            self.processing_tab.height_spin.setValue(1000)
            self.processing_tab.dpi_spin.setValue(300)
            self.processing_tab.max_file_size_spin.setValue(2.0)
            self.setup_tab.suffix_edit.setText("_processed")
            self.setup_tab.set_source_formats(None)
            self.setup_tab.set_output_format(None)
            self._set_combo_data(self.processing_tab.units_combo, Units.PIXELS.value)
            self._set_combo_data(self.processing_tab.resize_mode_combo, ResizeMode.CONTAIN.value)
            self._set_combo_data(self.setup_tab.conflict_combo, ConflictStrategy.ADD_COUNTER.value)

        def _set_combo_data(self, combo, value: str | None) -> None:
            for index in range(combo.count()):
                if combo.itemData(index) == value:
                    combo.setCurrentIndex(index)
                    break

        def _apply_selected_preset(self) -> None:
            preset_id = self.setup_tab.preset_combo.currentData()
            if not preset_id:
                return
            preset = PRESETS[preset_id]
            self.processing_tab.width_spin.setValue(preset.width)
            self.processing_tab.height_spin.setValue(preset.height)
            self.processing_tab.dpi_spin.setValue(preset.dpi)
            self.processing_tab.max_file_size_spin.setValue(preset.max_file_size_mb)
            self._set_combo_data(self.processing_tab.units_combo, preset.units.value)
            self._set_combo_data(self.processing_tab.resize_mode_combo, preset.resize_mode.value)

        def _save_settings(self) -> None:
            settings = self._build_settings()
            self.settings_controller.save_settings(settings, self.setup_tab.preset_combo.currentData())
            self.statusBar().showMessage(self.translator.text("status.ready"))

        def _switch_language(self, language: str) -> None:
            self.translator.set_language(language)
            self._retranslate()

        def _show_help(self) -> None:
            QMessageBox.information(self, self.translator.text("menu.help.help"), self.translator.text("help.text"))

        def _show_about(self) -> None:
            QMessageBox.information(self, self.translator.text("menu.help.about"), self.translator.text("about.text"))

        def _retranslate(self) -> None:
            t = self.translator.text
            self.setWindowTitle(t("app.title"))
            self.language_menu.setTitle(t("menu.language"))
            self.help_menu.setTitle(t("menu.help"))
            self.help_action.setText(t("menu.help.help"))
            self.about_action.setText(t("menu.help.about"))
            self.lang_en_action.setText(t("lang.english"))
            self.lang_ru_action.setText(t("lang.russian"))
            self.lang_he_action.setText(t("lang.hebrew"))
            self.tabs.setTabText(0, t("tab.setup"))
            self.tabs.setTabText(1, t("tab.processing"))
            self.tabs.setTabText(2, t("tab.report"))
            self.setup_tab.retranslate(t)
            self.processing_tab.retranslate(t)
            self.report_tab.retranslate(t)
            self.preview_button.setText(t("actions.preview"))
            self.start_button.setText(t("actions.start"))
            self.open_output_button.setText(t("actions.open_output"))
            self.save_settings_button.setText(t("actions.save_settings"))

except ImportError:  # pragma: no cover - depends on environment
    class MainWindow:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("PySide6 is required to construct the GUI window.")
