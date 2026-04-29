from __future__ import annotations

from pathlib import Path

from photo_processor.core.settings import ResizeMode

try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPixmap
    from PySide6.QtWidgets import (
        QComboBox,
        QFormLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QPushButton,
        QScrollArea,
        QVBoxLayout,
        QWidget,
    )

    class ManualTab(QWidget):
        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._preview_pixmap = QPixmap()
            layout = QHBoxLayout(self)

            self.file_list = QListWidget(self)
            self.file_list.setMinimumWidth(260)

            right_panel = QWidget(self)
            right_layout = QVBoxLayout(right_panel)

            controls_group = QGroupBox(right_panel)
            controls_form = QFormLayout(controls_group)
            self.manual_resize_mode_combo = QComboBox(controls_group)
            for mode in ResizeMode:
                self.manual_resize_mode_combo.addItem("", mode.value)
            self.manual_resize_mode_label = QLabel(controls_group)
            controls_form.addRow(self.manual_resize_mode_label, self.manual_resize_mode_combo)

            info_group = QGroupBox(right_panel)
            info_form = QFormLayout(info_group)
            self.source_info_label_name = QLabel(info_group)
            self.source_info_value = QLabel(info_group)
            self.target_info_label_name = QLabel(info_group)
            self.target_info_value = QLabel(info_group)
            info_form.addRow(self.source_info_label_name, self.source_info_value)
            info_form.addRow(self.target_info_label_name, self.target_info_value)

            self.preview_scroll = QScrollArea(right_panel)
            self.preview_scroll.setWidgetResizable(True)
            self.preview_label = QLabel(self.preview_scroll)
            self.preview_label.setAlignment(Qt.AlignCenter)
            self.preview_label.setMinimumSize(320, 240)
            self.preview_scroll.setWidget(self.preview_label)

            actions_row = QHBoxLayout()
            self.previous_button = QPushButton(right_panel)
            self.next_button = QPushButton(right_panel)
            self.save_current_button = QPushButton(right_panel)
            actions_row.addWidget(self.previous_button)
            actions_row.addWidget(self.next_button)
            actions_row.addStretch(1)
            actions_row.addWidget(self.save_current_button)

            right_layout.addWidget(controls_group)
            right_layout.addWidget(info_group)
            right_layout.addWidget(self.preview_scroll, 1)
            right_layout.addLayout(actions_row)

            layout.addWidget(self.file_list)
            layout.addWidget(right_panel, 1)

        def set_file_list(self, files: list[Path]) -> None:
            current = self.current_file_name()
            self.file_list.clear()
            for path in files:
                self.file_list.addItem(path.name)
            if not files:
                self.preview_label.clear()
                self.source_info_value.clear()
                self.target_info_value.clear()
                return
            if current:
                for index, path in enumerate(files):
                    if path.name == current:
                        self.file_list.setCurrentRow(index)
                        return
            self.file_list.setCurrentRow(0)

        def current_file_name(self) -> str | None:
            item = self.file_list.currentItem()
            return item.text() if item is not None else None

        def set_preview_pixmap(self, pixmap) -> None:
            self._preview_pixmap = pixmap
            self._update_preview_pixmap()

        def clear_preview(self) -> None:
            self._preview_pixmap = QPixmap()
            self.preview_label.clear()
            self.source_info_value.clear()
            self.target_info_value.clear()

        def resizeEvent(self, event) -> None:
            super().resizeEvent(event)
            self._update_preview_pixmap()

        def _update_preview_pixmap(self) -> None:
            if self._preview_pixmap.isNull():
                self.preview_label.clear()
                return
            viewport_size = self.preview_scroll.viewport().size()
            scaled = self._preview_pixmap.scaled(
                max(1, viewport_size.width() - 12),
                max(1, viewport_size.height() - 12),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.preview_label.setPixmap(scaled)
            self.preview_label.resize(scaled.size())

        def retranslate(self, t) -> None:
            self.manual_resize_mode_label.setText(t("manual.resize_mode"))
            for idx, mode in enumerate(ResizeMode):
                self.manual_resize_mode_combo.setItemText(idx, t(f"resize_mode.{mode.value}"))
            self.source_info_label_name.setText(t("manual.source_info"))
            self.target_info_label_name.setText(t("manual.target_info"))
            self.previous_button.setText(t("manual.previous"))
            self.next_button.setText(t("manual.next"))
            self.save_current_button.setText(t("manual.save_current"))

except ImportError:  # pragma: no cover - depends on environment
    class ManualTab:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("PySide6 is required to construct GUI tabs.")
