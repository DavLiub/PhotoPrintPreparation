from __future__ import annotations

from photo_processor.config.presets import PRESETS

try:
    from PySide6.QtWidgets import QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget

    class SourceTab(QWidget):
        def __init__(self, preset_changed_callback, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            layout = QVBoxLayout(self)
            self.group = QGroupBox(self)
            form = QFormLayout(self.group)

            self.source_path_edit = QLineEdit(self.group)
            self.source_browse_button = QPushButton(self.group)
            source_row_widget = QWidget(self.group)
            source_row = QHBoxLayout(source_row_widget)
            source_row.setContentsMargins(0, 0, 0, 0)
            source_row.addWidget(self.source_path_edit)
            source_row.addWidget(self.source_browse_button)

            self.preset_combo = QComboBox(self.group)
            self.preset_combo.addItem("", None)
            for preset_id, preset in PRESETS.items():
                self.preset_combo.addItem(preset.display_name, preset_id)
            self.preset_combo.currentIndexChanged.connect(preset_changed_callback)

            form.addRow("", source_row_widget)
            form.addRow("", self.preset_combo)
            self.source_folder_label = form.labelForField(source_row_widget)
            self.preset_label = form.labelForField(self.preset_combo)
            layout.addWidget(self.group)
            layout.addStretch(1)

        def retranslate(self, t) -> None:
            self.group.setTitle(t("source.group"))
            self.source_folder_label.setText(t("source.folder"))
            self.source_browse_button.setText(t("source.browse"))
            self.preset_label.setText(t("source.preset"))
            self.preset_combo.setItemText(0, t("preset.none"))

except ImportError:  # pragma: no cover - depends on environment
    class SourceTab:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("PySide6 is required to construct GUI tabs.")
