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
            self._no_preview_text = "Select a file to preview."
            self._no_files_text = "No matching files"
            layout = QHBoxLayout(self)

            files_group = QGroupBox(self)
            files_layout = QVBoxLayout(files_group)
            self.file_count_label = QLabel(files_group)
            self.file_count_label.setStyleSheet("color: #475569; font-size: 12px; font-weight: 600;")
            self.file_list = QListWidget(files_group)
            self.file_list.setMinimumWidth(260)
            self.file_list.currentRowChanged.connect(self._update_navigation_state)
            files_layout.addWidget(self.file_count_label)
            files_layout.addWidget(self.file_list, 1)

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
            self.selected_file_label_name = QLabel(info_group)
            self.selected_file_value = QLabel(info_group)
            self.source_info_label_name = QLabel(info_group)
            self.source_info_value = QLabel(info_group)
            self.target_info_label_name = QLabel(info_group)
            self.target_info_value = QLabel(info_group)
            self.output_file_label_name = QLabel(info_group)
            self.output_file_value = QLabel(info_group)
            self.selected_file_value.setWordWrap(True)
            self.source_info_value.setWordWrap(True)
            self.target_info_value.setWordWrap(True)
            self.output_file_value.setWordWrap(True)
            info_form.addRow(self.selected_file_label_name, self.selected_file_value)
            info_form.addRow(self.source_info_label_name, self.source_info_value)
            info_form.addRow(self.target_info_label_name, self.target_info_value)
            info_form.addRow(self.output_file_label_name, self.output_file_value)

            self.preview_scroll = QScrollArea(right_panel)
            self.preview_scroll.setWidgetResizable(True)
            self.preview_label = QLabel(self.preview_scroll)
            self.preview_label.setAlignment(Qt.AlignCenter)
            self.preview_label.setMinimumSize(320, 240)
            self.preview_label.setWordWrap(True)
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

            layout.addWidget(files_group)
            layout.addWidget(right_panel, 1)
            self._update_navigation_state()

        def set_file_list(self, files: list[Path]) -> None:
            current = self.current_file_name()
            self.file_list.clear()
            for path in files:
                self.file_list.addItem(path.name)
            if not files:
                self.clear_preview()
                self.file_count_label.setText(self._no_files_label())
                self._update_navigation_state()
                return
            self.file_count_label.setText(self._file_count_text(self.file_list.currentRow(), len(files)))
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
            self._update_navigation_state()

        def clear_preview(self) -> None:
            self._preview_pixmap = QPixmap()
            self.preview_label.setText(self._no_preview_text)
            self.selected_file_value.clear()
            self.source_info_value.clear()
            self.target_info_value.clear()
            self.output_file_value.clear()
            self._update_navigation_state()

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
            self.preview_label.setText("")
            self.preview_label.setPixmap(scaled)
            self.preview_label.resize(scaled.size())

        def set_preview_metadata(
            self,
            *,
            selected_file: str,
            source_info: str,
            target_info: str,
            output_file: str,
            current_index: int,
            total_files: int,
        ) -> None:
            self.selected_file_value.setText(selected_file)
            self.source_info_value.setText(source_info)
            self.target_info_value.setText(target_info)
            self.output_file_value.setText(output_file)
            self.file_count_label.setText(self._file_count_text(current_index, total_files))
            self._update_navigation_state()

        def _update_navigation_state(self, *_args) -> None:
            row = self.file_list.currentRow()
            total = self.file_list.count()
            has_selection = 0 <= row < total
            self.previous_button.setEnabled(has_selection and row > 0)
            self.next_button.setEnabled(has_selection and row < total - 1)
            self.save_current_button.setEnabled(has_selection)

        def _no_preview_label(self) -> str:
            return self._no_preview_text

        def _no_files_label(self) -> str:
            return self._no_files_text

        def _file_count_text(self, row: int, total: int) -> str:
            if total <= 0:
                return self._no_files_label()
            current = max(0, row) + 1 if row >= 0 else 0
            return f"{current}/{total}"

        def retranslate(self, t) -> None:
            self._no_preview_text = t("manual.no_preview")
            self._no_files_text = t("manual.no_files")
            self.file_count_label.setText(self._file_count_text(self.file_list.currentRow(), self.file_list.count()))
            self.manual_resize_mode_label.setText(t("manual.resize_mode"))
            for idx, mode in enumerate(ResizeMode):
                self.manual_resize_mode_combo.setItemText(idx, t(f"resize_mode.{mode.value}"))
            self.selected_file_label_name.setText(t("manual.selected_file"))
            self.source_info_label_name.setText(t("manual.source_info"))
            self.target_info_label_name.setText(t("manual.target_info"))
            self.output_file_label_name.setText(t("manual.output_file"))
            self.previous_button.setText(t("manual.previous"))
            self.next_button.setText(t("manual.next"))
            self.save_current_button.setText(t("manual.save_current"))
            if self._preview_pixmap.isNull():
                self.preview_label.setText(self._no_preview_text)
            if self.file_list.count() == 0:
                self.file_count_label.setText(self._no_files_text)

except ImportError:  # pragma: no cover - depends on environment
    class ManualTab:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("PySide6 is required to construct GUI tabs.")
