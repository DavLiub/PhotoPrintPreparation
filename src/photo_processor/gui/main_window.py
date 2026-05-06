from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from photo_processor.app.controllers.processing_controller import ProcessingController
from photo_processor.app.controllers.settings_controller import SettingsController
from photo_processor.app.i18n.translator import Translator
from photo_processor.app.use_cases.connect_google_drive import ConnectGoogleDriveUseCase, GoogleDriveConnection
from photo_processor.app.use_cases.disconnect_google_drive import DisconnectGoogleDriveUseCase
from photo_processor.config.presets import PRESETS
from photo_processor.core.cloud_upload import CloudProvider, CloudUploadSettings
from photo_processor.core.image_task import ImageTask
from photo_processor.core.output_policy import ConflictStrategy
from photo_processor.core.settings import CropAnchor, ProcessingSettings, ResizeMode, Units
from photo_processor.gui.dialogs.about_dialog import AboutDialog
from photo_processor.gui.dialogs.google_drive_folder_browser_dialog import GoogleDriveFolderBrowserDialog
from photo_processor.gui.dialogs.help_dialog import HelpDialog
from photo_processor.gui.google_drive_connect_worker import GoogleDriveConnectWorker
from photo_processor.gui.icon_provider import (
    about_icon_path,
    app_icon_path,
    build_icon,
    flag_en_path,
    flag_he_path,
    flag_ru_path,
    help_icon_path,
)
from photo_processor.gui.image_preview import pil_image_to_qpixmap
from photo_processor.gui.processing_worker import ProcessingWorker
from photo_processor.gui.tabs.manual_tab import ManualTab
from photo_processor.gui.tabs.processing_tab import ProcessingTab
from photo_processor.gui.tabs.report_tab import ReportTab
from photo_processor.gui.tabs.setup_tab import SetupTab
from photo_processor.infra.cloud.google_drive_credentials_resolver import GoogleDriveCredentialsResolver
from photo_processor.infra.cloud.google_drive_oauth import GoogleDriveOAuthFlow
from photo_processor.infra.cloud.google_drive_uploader import GoogleDriveUploader
from photo_processor.infra.filesystem.file_scanner import scan_supported_images
from photo_processor.infra.filesystem.output_path_builder import build_output_path
from photo_processor.infra.imaging.image_processor import ImageProcessor
from photo_processor.infra.imaging.manual_preview import build_manual_preview
from photo_processor.infra.secrets.windows_dpapi_store import WindowsDPAPISecretStore
from photo_processor.infra.settings_storage.storage_paths import resolve_secret_store_dir

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
            self.cloud_connect_thread: QThread | None = None
            self.cloud_connect_worker: GoogleDriveConnectWorker | None = None
            self.processing_dry_run = False
            self.current_run_settings: ProcessingSettings | None = None
            self.manual_files: list[Path] = []
            self.source_count_enabled = False
            self.source_count_timer = QTimer(self)
            self.source_count_timer.setSingleShot(True)
            self.source_count_timer.setInterval(250)
            self.source_count_timer.timeout.connect(self._refresh_source_file_count)
            self.help_dialog: HelpDialog | None = None
            self.about_dialog: AboutDialog | None = None
            self.secret_store = WindowsDPAPISecretStore(resolve_secret_store_dir())
            self.google_drive_credentials_resolver = GoogleDriveCredentialsResolver(secret_store=self.secret_store)
            self._setup_ui()
            self._load_saved_snapshot()
            self._retranslate()

        def _setup_ui(self) -> None:
            self.setMinimumSize(980, 760)
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
            self.manual_tab = ManualTab(root)
            self.report_tab = ReportTab(root)
            self.tabs.addTab(self.setup_tab, "")
            self.tabs.addTab(self.processing_tab, "")
            self.tabs.addTab(self.manual_tab, "")
            self.tabs.addTab(self.report_tab, "")

            self.start_button = QPushButton(root)
            self.open_output_button = QPushButton(root)
            self.save_settings_button = QPushButton(root)
            self.progress_bar = QProgressBar(root)
            self.progress_bar.setMinimum(0)
            self.progress_bar.setValue(0)
            self.progress_count_label = QLabel(root)
            self.setup_tab.source_browse_button.clicked.connect(self._choose_source_folder)
            self.setup_tab.output_browse_button.clicked.connect(self._choose_output_folder)
            self.setup_tab.google_drive_button.clicked.connect(self._toggle_google_drive_connection)
            self.setup_tab.cloud_browse_button.clicked.connect(self._browse_google_drive_folder)
            self.setup_tab.source_path_edit.textEdited.connect(self._enable_source_count_refresh)
            self.setup_tab.source_path_edit.textChanged.connect(self._schedule_source_file_count_refresh)
            for checkbox in self.setup_tab.format_checkboxes.values():
                checkbox.toggled.connect(self._enable_source_count_refresh)
                checkbox.toggled.connect(self._schedule_source_file_count_refresh)
            self.processing_tab.width_spin.valueChanged.connect(self._refresh_manual_preview)
            self.processing_tab.height_spin.valueChanged.connect(self._refresh_manual_preview)
            self.processing_tab.units_combo.currentIndexChanged.connect(self._sync_manual_resize_mode_from_processing)
            self.processing_tab.dpi_spin.valueChanged.connect(self._refresh_manual_preview)
            self.processing_tab.auto_rotate_check.toggled.connect(self._refresh_manual_preview)
            self.processing_tab.resize_mode_combo.currentIndexChanged.connect(self._sync_manual_resize_mode_from_processing)
            self.processing_tab.crop_anchor_combo.currentIndexChanged.connect(self._refresh_manual_preview)
            self.manual_tab.file_list.currentRowChanged.connect(self._refresh_manual_preview)
            self.manual_tab.manual_resize_mode_combo.currentIndexChanged.connect(self._refresh_manual_preview)
            self.manual_tab.previous_button.clicked.connect(self._select_previous_manual_file)
            self.manual_tab.next_button.clicked.connect(self._select_next_manual_file)
            self.manual_tab.save_current_button.clicked.connect(self._save_current_manual_file)
            self.start_button.clicked.connect(self._start_processing)
            self.open_output_button.clicked.connect(self._open_output_folder)
            self.save_settings_button.clicked.connect(self._save_settings)
            self._style_action_buttons()
            actions_row = QHBoxLayout()
            actions_row.addWidget(self.start_button)
            actions_row.addWidget(self.progress_bar, 1)
            actions_row.addWidget(self.progress_count_label)
            actions_row.addSpacing(12)
            actions_row.addWidget(self.open_output_button)
            actions_row.addWidget(self.save_settings_button)

            layout.addWidget(self.tabs)
            layout.addLayout(actions_row)
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
            self.open_output_button.setStyleSheet(neutral_style)
            self.save_settings_button.setStyleSheet(neutral_style)
            self.start_button.setStyleSheet(primary_style)
            self.progress_count_label.setStyleSheet("color: #475569; font-size: 12px; font-weight: 600;")

        def _build_settings(self) -> ProcessingSettings:
            source_folder = Path(self.setup_tab.source_path_edit.text() or ".").resolve()
            output_folder = Path(self.setup_tab.output_path_edit.text() or (source_folder / "processed")).resolve()
            from photo_processor.core.output_policy import OutputPolicy

            return ProcessingSettings(
                source_folder=source_folder,
                output_folder=output_folder,
                width=float(self.processing_tab.width_spin.value()),
                height=float(self.processing_tab.height_spin.value()),
                units=Units(self.processing_tab.units_combo.currentData()),
                dpi=int(self.processing_tab.dpi_spin.value()),
                auto_rotate=self.processing_tab.auto_rotate_check.isChecked(),
                resize_mode=ResizeMode(self.processing_tab.resize_mode_combo.currentData()),
                crop_anchor=CropAnchor(self.processing_tab.crop_anchor_combo.currentData()),
                max_file_size_mb=float(self.processing_tab.max_file_size_spin.value()),
                source_formats=self.setup_tab.selected_source_formats(),
                cloud_upload=CloudUploadSettings(
                    enabled=self.setup_tab.cloud_enabled_check.isChecked(),
                    provider=self.setup_tab.selected_cloud_provider(),
                    connection_id=self.setup_tab.google_drive_button.property("connection_id"),
                    account_email=self.setup_tab.cloud_account_value.property("account_email"),
                    remote_folder=self.setup_tab.selected_cloud_remote_folder_id(),
                    remote_folder_display=self.setup_tab.selected_cloud_remote_folder_display(),
                ),
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
            self.processing_tab.auto_rotate_check.setChecked(True if snapshot.auto_rotate is None else snapshot.auto_rotate)
            self.processing_tab.max_file_size_spin.setValue(snapshot.max_file_size_mb or 2.0)
            self.setup_tab.suffix_edit.setText(snapshot.filename_suffix or "_processed")
            self.setup_tab.set_source_formats(snapshot.source_formats)
            self.setup_tab.set_output_format(snapshot.output_format)
            self.setup_tab.cloud_enabled_check.setChecked(bool(snapshot.cloud_upload_enabled))
            self.setup_tab.set_cloud_remote_folder(
                snapshot.cloud_remote_folder,
                snapshot.cloud_remote_folder_display,
            )
            self._set_cloud_connection(snapshot.cloud_connection_id, snapshot.cloud_account_email)
            self._set_combo_data(self.processing_tab.units_combo, snapshot.units or Units.PIXELS.value)
            self._set_combo_data(self.processing_tab.resize_mode_combo, snapshot.resize_mode or ResizeMode.CONTAIN.value)
            self._set_combo_data(self.manual_tab.manual_resize_mode_combo, snapshot.resize_mode or ResizeMode.CONTAIN.value)
            self._set_combo_data(self.processing_tab.crop_anchor_combo, snapshot.crop_anchor or CropAnchor.TOP_LEFT.value)
            self._set_combo_data(self.setup_tab.conflict_combo, snapshot.conflict_strategy or ConflictStrategy.ADD_COUNTER.value)
            if snapshot.preset_id:
                self._set_combo_data(self.setup_tab.preset_combo, snapshot.preset_id)
            self._reset_session_views(enable_source_count=bool(snapshot.source_folder))

        def _apply_defaults(self) -> None:
            self.processing_tab.width_spin.setValue(1500)
            self.processing_tab.height_spin.setValue(1000)
            self.processing_tab.dpi_spin.setValue(300)
            self.processing_tab.auto_rotate_check.setChecked(True)
            self.processing_tab.max_file_size_spin.setValue(2.0)
            self.setup_tab.suffix_edit.setText("_processed")
            self.setup_tab.set_source_formats(None)
            self.setup_tab.set_output_format(None)
            self.setup_tab.cloud_enabled_check.setChecked(False)
            self.setup_tab.set_cloud_remote_folder(None, None)
            self._set_cloud_connection(None, None)
            self._set_combo_data(self.processing_tab.units_combo, Units.PIXELS.value)
            self._set_combo_data(self.processing_tab.resize_mode_combo, ResizeMode.CONTAIN.value)
            self._set_combo_data(self.manual_tab.manual_resize_mode_combo, ResizeMode.CONTAIN.value)
            self._set_combo_data(self.processing_tab.crop_anchor_combo, CropAnchor.TOP_LEFT.value)
            self._set_combo_data(self.setup_tab.conflict_combo, ConflictStrategy.ADD_COUNTER.value)
            self._reset_session_views(enable_source_count=False)

        def _set_combo_data(self, combo, value: str | None) -> None:
            for index in range(combo.count()):
                if combo.itemData(index) == value:
                    combo.setCurrentIndex(index)
                    break

        def _set_cloud_connection(self, connection_id: str | None, account_email: str | None) -> None:
            self.setup_tab.google_drive_button.blockSignals(True)
            self.setup_tab.google_drive_button.setChecked(bool(connection_id))
            self.setup_tab.google_drive_button.blockSignals(False)
            self.setup_tab.google_drive_button.setProperty("connection_id", connection_id)
            self.setup_tab.cloud_account_value.setProperty("account_email", account_email)
            self.setup_tab.set_cloud_account_text(account_email or self.translator.text("cloud.status.not_connected"))
            self.setup_tab.update_connection_status(bool(connection_id), self.translator.text)
            self._refresh_cloud_action_availability()

        def _refresh_cloud_action_availability(self, *_args) -> None:
            is_busy = self.processing_thread is not None or self.cloud_connect_thread is not None
            has_connection = bool(self.setup_tab.google_drive_button.property("connection_id"))
            self.setup_tab.google_drive_button.setEnabled(not is_busy)
            self.setup_tab.cloud_browse_button.setEnabled(not is_busy and has_connection)

        def _apply_selected_preset(self) -> None:
            preset_id = self.setup_tab.preset_combo.currentData()
            if not preset_id:
                return
            preset = PRESETS[preset_id]
            self.processing_tab.width_spin.setValue(preset.width)
            self.processing_tab.height_spin.setValue(preset.height)
            self.processing_tab.dpi_spin.setValue(preset.dpi)
            self.processing_tab.auto_rotate_check.setChecked(preset.auto_rotate)
            self.processing_tab.max_file_size_spin.setValue(preset.max_file_size_mb)
            self._set_combo_data(self.processing_tab.units_combo, preset.units.value)
            self._set_combo_data(self.processing_tab.resize_mode_combo, preset.resize_mode.value)
            self._set_combo_data(self.manual_tab.manual_resize_mode_combo, preset.resize_mode.value)

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

        def _browse_google_drive_folder(self) -> None:
            t = self.translator.text
            if not self.setup_tab.google_drive_button.property("connection_id"):
                QMessageBox.information(
                    self,
                    t("dialog.cloud_browse.title"),
                    t("dialog.cloud_browse.not_connected"),
                )
                return
            try:
                settings = self._build_settings()
                credentials = self.google_drive_credentials_resolver.resolve(settings)
                dialog = GoogleDriveFolderBrowserDialog(
                    uploader=GoogleDriveUploader(credentials),
                    t=t,
                    initial_folder_id=self.setup_tab.selected_cloud_remote_folder_id(),
                    parent=self,
                )
            except Exception as exc:
                QMessageBox.critical(
                    self,
                    t("dialog.cloud_browse.failed.title"),
                    str(exc),
                )
                return
            if dialog.exec():
                selected_folder_id = dialog.selected_folder_id()
                if selected_folder_id:
                    self.setup_tab.set_cloud_remote_folder(
                        selected_folder_id,
                        dialog.selected_folder_path(),
                    )
                self._save_settings()
                self.statusBar().showMessage(
                    t("status.cloud_folder_selected").format(
                        name=dialog.selected_folder_path() or dialog.selected_folder_name() or selected_folder_id or "root"
                    )
                )

        def _toggle_google_drive_connection(self, is_checked: bool) -> None:
            if is_checked:
                self._connect_google_drive()
                return
            self._disconnect_google_drive()

        def _connect_google_drive(self) -> None:
            self._set_cloud_connect_state(True)
            self.statusBar().showMessage(self.translator.text("status.cloud_connecting"))
            use_case = ConnectGoogleDriveUseCase(
                oauth_flow=GoogleDriveOAuthFlow(),
                credentials_resolver=self.google_drive_credentials_resolver,
            )
            self.cloud_connect_thread = QThread(self)
            self.cloud_connect_worker = GoogleDriveConnectWorker(use_case)
            self.cloud_connect_worker.moveToThread(self.cloud_connect_thread)
            self.cloud_connect_thread.started.connect(self.cloud_connect_worker.run)
            self.cloud_connect_worker.finished.connect(self._handle_cloud_connect_finished)
            self.cloud_connect_worker.failed.connect(self._handle_cloud_connect_failed)
            self.cloud_connect_worker.finished.connect(self.cloud_connect_thread.quit)
            self.cloud_connect_worker.failed.connect(self.cloud_connect_thread.quit)
            self.cloud_connect_thread.finished.connect(self._cleanup_cloud_connect_thread)
            self.cloud_connect_thread.start()

        def _disconnect_google_drive(self) -> None:
            DisconnectGoogleDriveUseCase(self.google_drive_credentials_resolver).run(
                self.setup_tab.google_drive_button.property("connection_id")
            )
            self._set_cloud_connection(None, None)
            self._save_settings()
            self.statusBar().showMessage(self.translator.text("status.cloud_disconnected"))

        def _handle_cloud_connect_finished(self, connection: GoogleDriveConnection) -> None:
            self._set_cloud_connect_state(False)
            self.setup_tab.cloud_enabled_check.setChecked(True)
            self._set_cloud_connection(connection.connection_id, connection.account_email)
            self._save_settings()
            self.statusBar().showMessage(self.translator.text("status.cloud_connected"))

        def _handle_cloud_connect_failed(self, message: str) -> None:
            self._set_cloud_connect_state(False)
            self._set_cloud_connection(None, None)
            QMessageBox.critical(
                self,
                self.translator.text("dialog.cloud_connect_failed.title"),
                message,
            )

        def _cleanup_cloud_connect_thread(self) -> None:
            if self.cloud_connect_worker is not None:
                self.cloud_connect_worker.deleteLater()
            if self.cloud_connect_thread is not None:
                self.cloud_connect_thread.deleteLater()
            self.cloud_connect_worker = None
            self.cloud_connect_thread = None
            self._refresh_cloud_action_availability()

        def _set_cloud_connect_state(self, is_connecting: bool) -> None:
            self.setup_tab.cloud_enabled_check.setEnabled(not is_connecting)
            self.setup_tab.cloud_remote_folder_edit.setEnabled(not is_connecting)
            self._refresh_cloud_action_availability()

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
                f"Uploaded: {report.uploaded_files}",
                f"Upload skipped: {report.upload_skipped_files}",
                f"Upload errors: {report.upload_error_files}",
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
                    upload_suffix = ""
                    if item.upload_result is not None:
                        upload_target = item.upload_result.remote_url or item.upload_result.remote_path or item.upload_result.file_id or "-"
                        upload_suffix = f" | upload {item.upload_result.status.value}:{upload_target}"
                    lines.append(
                        f"{item.status.value.upper():7} {source_name}{size_suffix}{output_suffix}{file_size_suffix}{quality_suffix}{upload_suffix}"
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
                        "Errors: 1",
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
            self.start_button.setEnabled(not is_running)
            self.open_output_button.setEnabled(not is_running)
            self.save_settings_button.setEnabled(not is_running)
            self.setup_tab.source_browse_button.setEnabled(not is_running)
            self.setup_tab.output_browse_button.setEnabled(not is_running)
            self.manual_tab.save_current_button.setEnabled(not is_running)
            self.tabs.setEnabled(not is_running)
            self._refresh_cloud_action_availability()
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
                self.manual_files = []
                self.manual_tab.set_file_list([])
                return
            source_folder = Path(source_text).expanduser()
            self.manual_files = scan_supported_images(source_folder, self.setup_tab.selected_source_formats())
            self.manual_tab.set_file_list(self.manual_files)
            total = len(self.manual_files)
            self._update_progress(0, total)
            self._refresh_manual_preview()

        def _sync_manual_resize_mode_from_processing(self) -> None:
            self._set_combo_data(
                self.manual_tab.manual_resize_mode_combo,
                self.processing_tab.resize_mode_combo.currentData(),
            )
            self._refresh_manual_preview()

        def _manual_preview_settings(self) -> ProcessingSettings:
            settings = self._build_settings()
            return replace(
                settings,
                resize_mode=ResizeMode(self.manual_tab.manual_resize_mode_combo.currentData()),
            )

        def _selected_manual_path(self) -> Path | None:
            row = self.manual_tab.file_list.currentRow()
            if row < 0 or row >= len(self.manual_files):
                return None
            return self.manual_files[row]

        def _refresh_manual_preview(self) -> None:
            source_path = self._selected_manual_path()
            if source_path is None:
                self.manual_tab.clear_preview()
                return
            try:
                preview_settings = self._manual_preview_settings()
                image, source_info, target_size, target_info = build_manual_preview(
                    source_path,
                    preview_settings,
                )
            except Exception:
                self.manual_tab.clear_preview()
                return
            pixmap = pil_image_to_qpixmap(image)
            self.manual_tab.set_preview_pixmap(pixmap)
            output_path = build_output_path(source_path, preview_settings.output_folder, preview_settings.output_policy)
            self.manual_tab.set_preview_metadata(
                selected_file=source_path.name,
                source_info=f"{source_info.width}x{source_info.height} | {source_info.mode} | {source_info.image_format or '-'}",
                target_info=f"{target_size[0]}x{target_size[1]} | {target_info.mode}",
                output_file=output_path.name if output_path is not None else self.translator.text("manual.output_skipped"),
                current_index=self.manual_tab.file_list.currentRow(),
                total_files=len(self.manual_files),
            )

        def _select_previous_manual_file(self) -> None:
            row = self.manual_tab.file_list.currentRow()
            if row > 0:
                self.manual_tab.file_list.setCurrentRow(row - 1)

        def _select_next_manual_file(self) -> None:
            row = self.manual_tab.file_list.currentRow()
            if 0 <= row < self.manual_tab.file_list.count() - 1:
                self.manual_tab.file_list.setCurrentRow(row + 1)

        def _save_current_manual_file(self) -> None:
            source_path = self._selected_manual_path()
            if source_path is None:
                return
            settings = self._manual_preview_settings()
            output_path = build_output_path(source_path, settings.output_folder, settings.output_policy)
            if output_path is None:
                QMessageBox.information(
                    self,
                    self.translator.text("manual.save_skipped_title"),
                    self.translator.text("manual.save_skipped_message"),
                )
                return
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                result = ImageProcessor(settings).process(
                    ImageTask(source_path=source_path, output_path=output_path)
                )
            except Exception as exc:
                QMessageBox.critical(
                    self,
                    self.translator.text("dialog.processing_failed.title"),
                    str(exc),
                )
                return
            self.statusBar().showMessage(f"Saved {result.output_path.name}")
            self._refresh_source_file_count()

        def _reset_session_views(self, enable_source_count: bool) -> None:
            self.source_count_timer.stop()
            self.source_count_enabled = enable_source_count
            self.report_tab.clear_report()
            self.manual_files = []
            self.manual_tab.set_file_list([])
            self.manual_tab.clear_preview()
            if enable_source_count:
                self._refresh_source_file_count()
            else:
                self._update_progress(0, 0)

        def closeEvent(self, event: QCloseEvent) -> None:
            if self.processing_thread is not None or self.cloud_connect_thread is not None:
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
            self.tabs.setTabText(2, t("tab.manual"))
            self.tabs.setTabText(3, t("tab.report"))
            self.setup_tab.retranslate(t)
            self._set_cloud_connection(
                self.setup_tab.google_drive_button.property("connection_id"),
                self.setup_tab.cloud_account_value.property("account_email"),
            )
            self.processing_tab.retranslate(t)
            self.manual_tab.retranslate(t)
            self.report_tab.retranslate(t)
            self.start_button.setText(t("actions.start"))
            self.open_output_button.setText(t("actions.open_output"))
            self.save_settings_button.setText(t("actions.save_settings"))

except ImportError:  # pragma: no cover - depends on environment
    class MainWindow:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("PySide6 is required to construct the GUI window.")
