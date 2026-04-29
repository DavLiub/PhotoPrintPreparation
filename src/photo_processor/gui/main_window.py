from __future__ import annotations

from pathlib import Path

from photo_processor.app.controllers.processing_controller import ProcessingController
from photo_processor.app.controllers.settings_controller import SettingsController
from photo_processor.app.i18n.translator import Translator
from photo_processor.config.presets import PRESETS
from photo_processor.core.output_policy import ConflictStrategy
from photo_processor.core.settings import ProcessingSettings, ResizeMode, Units
from photo_processor.gui.dialogs.about_dialog import AboutDialog
from photo_processor.gui.dialogs.help_dialog import HelpDialog
from photo_processor.gui.icon_provider import (
    about_icon_path,
    app_icon_path,
    build_icon,
    flag_en_path,
    flag_he_path,
    flag_ru_path,
    help_icon_path,
)
from photo_processor.gui.processing_worker import ProcessingWorker
from photo_processor.gui.tabs.processing_tab import ProcessingTab
from photo_processor.gui.tabs.report_tab import ReportTab
from photo_processor.gui.tabs.setup_tab import SetupTab
from photo_processor.infra.filesystem.file_scanner import scan_supported_images

try:
    from PySide6.QtCore import QThread, QTimer, QUrl
    from PySide6.QtGui import QAction, QCloseEvent, QDesktopServices
    from PySide6.QtWidgets import (
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMenu,
        QMenuBar,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QStatusBar,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )

    class MainWindow(QMainWindow):
        def __init__(
            self,
            translator: Translator,
            settings_controller: SettingsController,
            processing_controller: ProcessingController,
        ) -> None:
            super().__init__()
            self.translator = translator
            self.settings_controller = settings_controller
            self.processing_controller = processing_controller
            self.processing_thread: QThread | None = None
            self.processing_worker: ProcessingWorker | None = None
            self.processing_dry_run = False
            self.current_run_settings: ProcessingSettings | None = None
            self.source_count_enabled = False
            self.source_count_timer = QTimer(self)
            self.source_count_timer.setSingleShot(True)
            self.source_count_timer.setInterval(250)
            self.source_count_timer.timeout.connect(self._refresh_source_file_count)
            self.help_dialog: HelpDialog | None = None
            self.about_dialog: AboutDialog | None = None
            self._setup_ui()
            self._load_saved_snapshot()
            self._retranslate()

        def _setup_ui(self) -> None:
            self.setMinimumSize(980, 680)
            self.setWindowIcon(build_icon(app_icon_path()))
            self._build_menu()
            self._build_central_widget()
            self.setStatusBar(QStatusBar(self))
            self.report_tab.clear_report()

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
            self.help_action.setIcon(build_icon(help_icon_path()))
            self.about_action.setIcon(build_icon(about_icon_path()))
            self.lang_en_action.setIcon(build_icon(flag_en_path()))
            self.lang_ru_action.setIcon(build_icon(flag_ru_path()))
            self.lang_he_action.setIcon(build_icon(flag_he_path()))
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
            self.progress_bar = QProgressBar(root)
            self.progress_bar.setMinimum(0)
            self.progress_bar.setValue(0)
            self.progress_count_label = QLabel(root)
            self.setup_tab.source_browse_button.clicked.connect(self._choose_source_folder)
            self.setup_tab.output_browse_button.clicked.connect(self._choose_output_folder)
            self.setup_tab.source_path_edit.textEdited.connect(self._enable_source_count_refresh)
            self.setup_tab.source_path_edit.textChanged.connect(self._schedule_source_file_count_refresh)
            for checkbox in self.setup_tab.format_checkboxes.values():
                checkbox.toggled.connect(self._enable_source_count_refresh)
                checkbox.toggled.connect(self._schedule_source_file_count_refresh)
            self.preview_button.clicked.connect(self._preview_processing)
            self.start_button.clicked.connect(self._start_processing)
            self.open_output_button.clicked.connect(self._open_output_folder)
            self.save_settings_button.clicked.connect(self._save_settings)
            self._style_action_buttons()
            actions_row.addWidget(self.preview_button)
            actions_row.addWidget(self.open_output_button)
            actions_row.addStretch(1)
            actions_row.addWidget(self.save_settings_button)

            run_row = QHBoxLayout()
            run_row.addWidget(self.start_button)
            run_row.addWidget(self.progress_bar, 1)
            run_row.addWidget(self.progress_count_label)

            layout.addWidget(self.tabs)
            layout.addLayout(actions_row)
            layout.addLayout(run_row)
            self.setCentralWidget(root)
            self._update_progress(0, 0)

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
            self.progress_count_label.setStyleSheet("color: #475569; font-size: 12px; font-weight: 600;")

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
            self._reset_session_views(enable_source_count=bool(snapshot.source_folder))

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
            self._reset_session_views(enable_source_count=False)

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
            self.statusBar().showMessage(self.translator.text("status.settings_saved"))

        def _switch_language(self, language: str) -> None:
            self.translator.set_language(language)
            self._retranslate()

        def _choose_source_folder(self) -> None:
            folder = QFileDialog.getExistingDirectory(
                self,
                self.translator.text("dialog.source.title"),
                self.setup_tab.source_path_edit.text() or str(Path.cwd()),
            )
            if folder:
                self.source_count_enabled = True
                self.setup_tab.source_path_edit.setText(folder)

        def _choose_output_folder(self) -> None:
            folder = QFileDialog.getExistingDirectory(
                self,
                self.translator.text("dialog.output.title"),
                self.setup_tab.output_path_edit.text() or self.setup_tab.source_path_edit.text() or str(Path.cwd()),
            )
            if folder:
                self.setup_tab.output_path_edit.setText(folder)

        def _preview_processing(self) -> None:
            self._run_processing(dry_run=True)

        def _start_processing(self) -> None:
            self._run_processing(dry_run=False)

        def _run_processing(self, dry_run: bool) -> None:
            settings = self._build_settings()
            if not settings.source_folder.exists():
                QMessageBox.warning(
                    self,
                    self.translator.text("dialog.validation.title"),
                    self.translator.text("dialog.validation.source_missing"),
                )
                return

            self.settings_controller.save_settings(settings, self.setup_tab.preset_combo.currentData())
            self.processing_dry_run = dry_run
            self.current_run_settings = settings
            self._set_processing_state(True)
            known_total = len(scan_supported_images(settings.source_folder, settings.source_formats))
            self._update_progress(0, known_total)
            self.processing_thread = QThread(self)
            self.processing_worker = ProcessingWorker(self.processing_controller, settings, dry_run)
            self.processing_worker.moveToThread(self.processing_thread)
            self.processing_thread.started.connect(self.processing_worker.run)
            self.processing_worker.progress.connect(self._update_progress)
            self.processing_worker.finished.connect(self._handle_processing_finished)
            self.processing_worker.failed.connect(self._handle_processing_failed)
            self.processing_worker.finished.connect(self.processing_thread.quit)
            self.processing_worker.failed.connect(self.processing_thread.quit)
            self.processing_thread.finished.connect(self._cleanup_processing_thread)
            self.processing_thread.start()

        def _format_report_text(self, settings, report, result) -> str:
            t = self.translator.text
            target_width, target_height = settings.target_size_px()
            lines = [
                t("report.summary"),
                f"Found files: {report.found_files}",
                f"Processed: {report.processed_files}",
                f"Skipped: {report.skipped_files}",
                f"Errors: {report.error_files}",
                f"Warnings: {report.warning_count}",
                "",
                t("report.context"),
                f"Source: {settings.source_folder}",
                f"Output: {settings.output_folder}",
                f"{t('report.target_frame')}: {target_width}x{target_height}",
                f"{t('report.resize_mode')}: {settings.resize_mode.value}",
                t("report.orientation_note").format(width=target_height, height=target_width),
            ]

            if result.items:
                lines.append("")
                lines.append(t("report.files"))
                for item in result.items:
                    source_name = item.source_path.name
                    source_size = ""
                    if item.source_info is not None:
                        source_size = f"{item.source_info.width}x{item.source_info.height}"
                    output_size = ""
                    if item.output_info is not None:
                        output_size = f"{item.output_info.width}x{item.output_info.height}"
                    size_suffix = f" | src {source_size}" if source_size else ""
                    output_suffix = f" | out {output_size}" if output_size else ""
                    file_size_suffix = ""
                    if item.output_file_size_bytes is not None:
                        file_size_suffix = f" | {round(item.output_file_size_bytes / 1024)} KB"
                    quality_suffix = ""
                    if item.output_quality is not None:
                        quality_suffix = f" | q={item.output_quality}"
                    lines.append(
                        f"{item.status.value.upper():7} {source_name}{size_suffix}{output_suffix}{file_size_suffix}{quality_suffix}"
                    )

            small_source_items = [
                item
                for item in result.items
                if any("smaller than the target frame" in warning for warning in item.warnings)
            ]
            if small_source_items:
                lines.append("")
                lines.append(t("report.warnings"))
                lines.append(t("report.warning.small_source_summary"))
                for item in small_source_items:
                    if item.source_info is None or item.target_size is None:
                        lines.append(f"- {item.source_path.name}")
                        continue
                    lines.append(
                        "- "
                        + t("report.warning.small_source_detail").format(
                            name=item.source_path.name,
                            source_width=item.source_info.width,
                            source_height=item.source_info.height,
                            target_width=item.target_size[0],
                            target_height=item.target_size[1],
                        )
                    )
            return "\n".join(lines)

        def _handle_processing_finished(self, execution) -> None:
            settings = self.current_run_settings
            if settings is None:
                self._handle_processing_failed(self.translator.text("dialog.processing_failed.message"))
                return
            self.report_tab.set_report_text(self._format_report_text(settings, execution.report, execution.result))
            self.tabs.setCurrentWidget(self.report_tab)
            self._set_processing_state(False)
            self._update_progress(execution.report.found_files, execution.report.found_files)
            status_key = "status.preview_ready" if self.processing_dry_run else "status.processing_complete"
            self.statusBar().showMessage(self.translator.text(status_key))

        def _handle_processing_failed(self, message: str) -> None:
            self._set_processing_state(False)
            self.report_tab.set_report_text(
                "\n".join(
                    [
                        self.translator.text("report.summary"),
                        f"Errors: 1",
                        "",
                        self.translator.text("report.warnings"),
                        message or self.translator.text("dialog.processing_failed.message"),
                    ]
                )
            )
            self.tabs.setCurrentWidget(self.report_tab)
            QMessageBox.critical(
                self,
                self.translator.text("dialog.processing_failed.title"),
                message or self.translator.text("dialog.processing_failed.message"),
            )

        def _cleanup_processing_thread(self) -> None:
            if self.processing_worker is not None:
                self.processing_worker.deleteLater()
            if self.processing_thread is not None:
                self.processing_thread.deleteLater()
            self.processing_worker = None
            self.processing_thread = None
            self.current_run_settings = None

        def _set_processing_state(self, is_running: bool) -> None:
            self.preview_button.setEnabled(not is_running)
            self.start_button.setEnabled(not is_running)
            self.open_output_button.setEnabled(not is_running)
            self.save_settings_button.setEnabled(not is_running)
            self.setup_tab.source_browse_button.setEnabled(not is_running)
            self.setup_tab.output_browse_button.setEnabled(not is_running)
            self.tabs.setEnabled(not is_running)
            if is_running:
                self.statusBar().showMessage(self.translator.text("status.processing_started"))
            else:
                self._schedule_source_file_count_refresh()

        def _update_progress(self, current: int, total: int) -> None:
            safe_total = max(total, 0)
            self.progress_bar.setMaximum(max(safe_total, 1))
            self.progress_bar.setValue(min(current, max(safe_total, 1)))
            self.progress_count_label.setText(f"({current}/{safe_total})")

        def _schedule_source_file_count_refresh(self) -> None:
            if self.processing_thread is not None or not self.source_count_enabled:
                return
            self.source_count_timer.start()

        def _enable_source_count_refresh(self, *_args) -> None:
            self.source_count_enabled = True

        def _refresh_source_file_count(self) -> None:
            if self.processing_thread is not None or not self.source_count_enabled:
                return
            source_text = self.setup_tab.source_path_edit.text().strip()
            if not source_text:
                self._update_progress(0, 0)
                return
            source_folder = Path(source_text).expanduser()
            total = len(scan_supported_images(source_folder, self.setup_tab.selected_source_formats()))
            self._update_progress(0, total)

        def _reset_session_views(self, enable_source_count: bool) -> None:
            self.source_count_timer.stop()
            self.source_count_enabled = enable_source_count
            self.report_tab.clear_report()
            if enable_source_count:
                self._refresh_source_file_count()
            else:
                self._update_progress(0, 0)

        def closeEvent(self, event: QCloseEvent) -> None:
            if self.processing_thread is not None:
                QMessageBox.warning(
                    self,
                    self.translator.text("dialog.close_while_processing.title"),
                    self.translator.text("dialog.close_while_processing.message"),
                )
                event.ignore()
                return
            self.source_count_timer.stop()
            super().closeEvent(event)

        def _open_output_folder(self) -> None:
            output_folder = Path(self.setup_tab.output_path_edit.text() or self._build_settings().output_folder).resolve()
            output_folder.mkdir(parents=True, exist_ok=True)
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(output_folder)))

        def _show_help(self) -> None:
            if self.help_dialog is None:
                self.help_dialog = HelpDialog(self.translator, self)
            self.help_dialog.retranslate()
            self.help_dialog.show()
            self.help_dialog.raise_()
            self.help_dialog.activateWindow()

        def _show_about(self) -> None:
            if self.about_dialog is None:
                self.about_dialog = AboutDialog(self.translator, self)
            self.about_dialog.retranslate()
            self.about_dialog.show()
            self.about_dialog.raise_()
            self.about_dialog.activateWindow()

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
