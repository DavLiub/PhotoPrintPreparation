from __future__ import annotations

from photo_processor.core.output_policy import ConflictStrategy

try:
    from PySide6.QtWidgets import QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget

    class OutputTab(QWidget):
        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            layout = QVBoxLayout(self)
            self.group = QGroupBox(self)
            form = QFormLayout(self.group)

            self.output_path_edit = QLineEdit(self.group)
            self.output_browse_button = QPushButton(self.group)
            output_row_widget = QWidget(self.group)
            output_row = QHBoxLayout(output_row_widget)
            output_row.setContentsMargins(0, 0, 0, 0)
            output_row.addWidget(self.output_path_edit)
            output_row.addWidget(self.output_browse_button)

            self.suffix_edit = QLineEdit(self.group)
            self.conflict_combo = QComboBox(self.group)
            for strategy in ConflictStrategy:
                self.conflict_combo.addItem("", strategy.value)

            form.addRow("", output_row_widget)
            form.addRow("", self.suffix_edit)
            form.addRow("", self.conflict_combo)
            self.output_folder_label = form.labelForField(output_row_widget)
            self.suffix_label = form.labelForField(self.suffix_edit)
            self.conflict_label = form.labelForField(self.conflict_combo)
            layout.addWidget(self.group)
            layout.addStretch(1)

        def retranslate(self, t) -> None:
            self.group.setTitle(t("output.group"))
            self.output_folder_label.setText(t("output.folder"))
            self.output_browse_button.setText(t("output.browse"))
            self.suffix_label.setText(t("output.suffix"))
            self.conflict_label.setText(t("output.conflict_strategy"))
            for idx, strategy in enumerate(ConflictStrategy):
                self.conflict_combo.setItemText(idx, t(f"conflict.{strategy.value}"))

except ImportError:  # pragma: no cover - depends on environment
    class OutputTab:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("PySide6 is required to construct GUI tabs.")
