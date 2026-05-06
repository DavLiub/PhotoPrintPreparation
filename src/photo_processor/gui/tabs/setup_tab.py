from __future__ import annotations

from photo_processor.config.presets import PRESETS
from photo_processor.core.cloud_upload import CloudProvider
from photo_processor.core.output_policy import ConflictStrategy, OutputFormat
from photo_processor.core.settings import SUPPORTED_INPUT_FORMATS
from photo_processor.gui.icon_provider import build_icon, dropbox_logo_path, google_drive_logo_path

try:
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtWidgets import (
        QButtonGroup,
        QCheckBox,
        QComboBox,
        QFormLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QToolButton,
        QVBoxLayout,
        QWidget,
    )

    class SetupTab(QWidget):
        def __init__(self, preset_changed_callback, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            layout = QVBoxLayout(self)

            self.source_group = QGroupBox(self)
            source_form = QFormLayout(self.source_group)
            self.source_path_edit = QLineEdit(self.source_group)
            self.source_browse_button = QPushButton(self.source_group)
            source_row_widget = QWidget(self.source_group)
            source_row = QHBoxLayout(source_row_widget)
            source_row.setContentsMargins(0, 0, 0, 0)
            source_row.addWidget(self.source_path_edit)
            source_row.addWidget(self.source_browse_button)

            self.preset_combo = QComboBox(self.source_group)
            self.preset_combo.addItem("", None)
            for preset_id, preset in PRESETS.items():
                self.preset_combo.addItem(preset.display_name, preset_id)
            self.preset_combo.currentIndexChanged.connect(preset_changed_callback)

            self.source_folder_label = QLabel(self.source_group)
            self.preset_label = QLabel(self.source_group)
            self.source_formats_label = QLabel(self.source_group)
            formats_widget = QWidget(self.source_group)
            formats_row = QHBoxLayout(formats_widget)
            formats_row.setContentsMargins(0, 0, 0, 0)
            formats_row.setSpacing(12)
            self.format_checkboxes: dict[str, QCheckBox] = {}
            for extension in SUPPORTED_INPUT_FORMATS:
                checkbox = QCheckBox(extension.upper().lstrip("."), formats_widget)
                checkbox.setChecked(True)
                self.format_checkboxes[extension] = checkbox
                formats_row.addWidget(checkbox)
            formats_row.addStretch(1)
            source_form.addRow(self.source_folder_label, source_row_widget)
            source_form.addRow(self.preset_label, self.preset_combo)
            source_form.addRow(self.source_formats_label, formats_widget)

            self.output_group = QGroupBox(self)
            output_form = QFormLayout(self.output_group)
            self.output_path_edit = QLineEdit(self.output_group)
            self.output_browse_button = QPushButton(self.output_group)
            output_row_widget = QWidget(self.output_group)
            output_row = QHBoxLayout(output_row_widget)
            output_row.setContentsMargins(0, 0, 0, 0)
            output_row.addWidget(self.output_path_edit)
            output_row.addWidget(self.output_browse_button)

            self.suffix_edit = QLineEdit(self.output_group)
            self.output_format_combo = QComboBox(self.output_group)
            self.output_format_combo.addItem(".jpg", OutputFormat.JPEG.value)
            self.conflict_combo = QComboBox(self.output_group)
            for strategy in ConflictStrategy:
                self.conflict_combo.addItem("", strategy.value)

            self.output_folder_label = QLabel(self.output_group)
            self.suffix_label = QLabel(self.output_group)
            self.output_format_label = QLabel(self.output_group)
            self.conflict_label = QLabel(self.output_group)
            output_form.addRow(self.output_folder_label, output_row_widget)
            output_form.addRow(self.suffix_label, self.suffix_edit)
            output_form.addRow(self.output_format_label, self.output_format_combo)
            output_form.addRow(self.conflict_label, self.conflict_combo)

            self.cloud_group = QGroupBox(self)
            cloud_form = QFormLayout(self.cloud_group)
            self.cloud_enabled_check = QCheckBox(self.cloud_group)

            self.cloud_provider_widget = QWidget(self.cloud_group)
            self.cloud_provider_row = QHBoxLayout(self.cloud_provider_widget)
            self.cloud_provider_row.setContentsMargins(0, 0, 0, 0)
            self.cloud_provider_row.setSpacing(12)
            self.provider_button_group = QButtonGroup(self.cloud_group)
            self.provider_button_group.setExclusive(True)
            self.google_drive_button = self._build_provider_button(CloudProvider.GOOGLE_DRIVE, google_drive_logo_path())
            self.dropbox_button = self._build_provider_button(CloudProvider.DROPBOX, dropbox_logo_path())
            self.provider_button_group.addButton(self.google_drive_button)
            self.provider_button_group.addButton(self.dropbox_button)
            self.cloud_provider_row.addWidget(self.google_drive_button)
            self.cloud_provider_row.addWidget(self.dropbox_button)
            self.cloud_provider_row.addStretch(1)

            self.cloud_remote_folder_edit = QLineEdit(self.cloud_group)
            self.cloud_status_badge = QLabel(self.cloud_group)
            self.cloud_status_badge.setMinimumWidth(120)
            self.cloud_status_badge.setAlignment(self.cloud_status_badge.alignment())
            self.cloud_account_value = QLabel(self.cloud_group)
            self.cloud_connect_button = QPushButton(self.cloud_group)
            self.cloud_disconnect_button = QPushButton(self.cloud_group)
            cloud_actions_widget = QWidget(self.cloud_group)
            cloud_actions_row = QHBoxLayout(cloud_actions_widget)
            cloud_actions_row.setContentsMargins(0, 0, 0, 0)
            cloud_actions_row.setSpacing(10)
            cloud_actions_row.addWidget(self.cloud_connect_button)
            cloud_actions_row.addWidget(self.cloud_disconnect_button)
            cloud_actions_row.addStretch(1)

            self.cloud_enabled_label = QLabel(self.cloud_group)
            self.cloud_provider_label = QLabel(self.cloud_group)
            self.cloud_remote_folder_label = QLabel(self.cloud_group)
            self.cloud_status_label = QLabel(self.cloud_group)
            self.cloud_account_label = QLabel(self.cloud_group)
            cloud_form.addRow(self.cloud_enabled_label, self.cloud_enabled_check)
            cloud_form.addRow(self.cloud_provider_label, self.cloud_provider_widget)
            cloud_form.addRow(self.cloud_status_label, self.cloud_status_badge)
            cloud_form.addRow(self.cloud_account_label, self.cloud_account_value)
            cloud_form.addRow(self.cloud_remote_folder_label, self.cloud_remote_folder_edit)
            cloud_form.addRow(QWidget(self.cloud_group), cloud_actions_widget)

            layout.addWidget(self.source_group)
            layout.addWidget(self.output_group)
            layout.addWidget(self.cloud_group)
            layout.addStretch(1)

            self.set_cloud_provider(CloudProvider.GOOGLE_DRIVE.value)
            self._apply_cloud_styles()

        def _build_provider_button(self, provider: CloudProvider, icon_path: str) -> QToolButton:
            button = QToolButton(self.cloud_group)
            button.setCheckable(True)
            button.setProperty("provider", provider.value)
            button.setIcon(build_icon(icon_path))
            button.setIconSize(QSize(34, 34))
            button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            button.setMinimumHeight(58)
            return button

        def _apply_cloud_styles(self) -> None:
            provider_style = """
            QToolButton {
                min-width: 190px;
                padding: 10px 14px;
                border-radius: 14px;
                border: 1px solid #cbd5e1;
                background: #ffffff;
                text-align: left;
                font-size: 13px;
                font-weight: 700;
                color: #0f172a;
            }
            QToolButton:checked {
                border: 2px solid #2563eb;
                background: #eff6ff;
            }
            QToolButton:hover {
                background: #f8fafc;
            }
            """
            badge_style = """
            QLabel {
                padding: 6px 12px;
                border-radius: 999px;
                background: #e2e8f0;
                color: #0f172a;
                font-weight: 700;
            }
            """
            self.google_drive_button.setStyleSheet(provider_style)
            self.dropbox_button.setStyleSheet(provider_style)
            self.cloud_status_badge.setStyleSheet(badge_style)

        def retranslate(self, t) -> None:
            self.source_group.setTitle(t("source.group"))
            self.source_folder_label.setText(t("source.folder"))
            self.source_browse_button.setText(t("source.browse"))
            self.preset_label.setText(t("source.preset"))
            self.source_formats_label.setText(t("source.formats"))
            self.preset_combo.setItemText(0, t("preset.none"))

            self.output_group.setTitle(t("output.group"))
            self.output_folder_label.setText(t("output.folder"))
            self.output_browse_button.setText(t("output.browse"))
            self.suffix_label.setText(t("output.suffix"))
            self.output_format_label.setText(t("output.extension"))
            self.output_format_combo.setItemText(0, ".jpg")
            self.conflict_label.setText(t("output.conflict_strategy"))
            for idx, strategy in enumerate(ConflictStrategy):
                self.conflict_combo.setItemText(idx, t(f"conflict.{strategy.value}"))

            self.cloud_group.setTitle(t("cloud.group"))
            self.cloud_enabled_label.setText(t("cloud.enabled"))
            self.cloud_provider_label.setText(t("cloud.provider"))
            self.cloud_status_label.setText(t("cloud.connection_status"))
            self.cloud_account_label.setText(t("cloud.account"))
            self.cloud_remote_folder_label.setText(t("cloud.remote_folder"))
            self.cloud_connect_button.setText(t("cloud.connect"))
            self.cloud_disconnect_button.setText(t("cloud.disconnect"))
            self.google_drive_button.setText(t("cloud.provider.google_drive"))
            self.dropbox_button.setText(t("cloud.provider.dropbox"))
            self.update_connection_status(bool(self.cloud_account_value.property("account_email")), t)
            if not self.cloud_account_value.property("account_email"):
                self.cloud_account_value.setText(t("cloud.status.not_connected"))

        def update_connection_status(self, is_connected: bool, t) -> None:
            if is_connected:
                self.cloud_status_badge.setText(t("cloud.status.connected"))
                self.cloud_status_badge.setStyleSheet(
                    "QLabel { padding: 6px 12px; border-radius: 999px; background: #dcfce7; color: #166534; font-weight: 700; }"
                )
            else:
                self.cloud_status_badge.setText(t("cloud.status.not_connected"))
                self.cloud_status_badge.setStyleSheet(
                    "QLabel { padding: 6px 12px; border-radius: 999px; background: #e2e8f0; color: #0f172a; font-weight: 700; }"
                )

        def selected_source_formats(self) -> tuple[str, ...]:
            selected = tuple(
                extension
                for extension, checkbox in self.format_checkboxes.items()
                if checkbox.isChecked()
            )
            return selected or SUPPORTED_INPUT_FORMATS

        def set_source_formats(self, formats: tuple[str, ...] | None) -> None:
            selected = set(formats or SUPPORTED_INPUT_FORMATS)
            for extension, checkbox in self.format_checkboxes.items():
                checkbox.setChecked(extension in selected)

        def selected_output_format(self) -> OutputFormat:
            return OutputFormat(self.output_format_combo.currentData())

        def set_output_format(self, output_format: str | None) -> None:
            target = output_format or OutputFormat.JPEG.value
            for index in range(self.output_format_combo.count()):
                if self.output_format_combo.itemData(index) == target:
                    self.output_format_combo.setCurrentIndex(index)
                    break

        def selected_cloud_provider(self) -> CloudProvider | None:
            if self.google_drive_button.isChecked():
                return CloudProvider.GOOGLE_DRIVE
            if self.dropbox_button.isChecked():
                return CloudProvider.DROPBOX
            return None

        def set_cloud_provider(self, provider: str | None) -> None:
            target = provider or CloudProvider.GOOGLE_DRIVE.value
            self.google_drive_button.setChecked(target == CloudProvider.GOOGLE_DRIVE.value)
            self.dropbox_button.setChecked(target == CloudProvider.DROPBOX.value)

        def set_cloud_account_text(self, text: str) -> None:
            self.cloud_account_value.setText(text)

except ImportError:  # pragma: no cover - depends on environment
    class SetupTab:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("PySide6 is required to construct GUI tabs.")
