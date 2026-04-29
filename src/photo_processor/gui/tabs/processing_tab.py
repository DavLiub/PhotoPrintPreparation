from __future__ import annotations

from photo_processor.core.settings import ResizeMode, Units

try:
    from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QFormLayout, QGroupBox, QLabel, QSpinBox, QVBoxLayout, QWidget

    class ProcessingTab(QWidget):
        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            layout = QVBoxLayout(self)
            self.group = QGroupBox(self)
            form = QFormLayout(self.group)

            self.units_combo = QComboBox(self.group)
            self.units_combo.addItem("", Units.PIXELS.value)
            self.units_combo.addItem("", Units.CENTIMETERS.value)
            self.width_spin = QDoubleSpinBox(self.group)
            self.width_spin.setMaximum(100000)
            self.height_spin = QDoubleSpinBox(self.group)
            self.height_spin.setMaximum(100000)
            self.dpi_spin = QSpinBox(self.group)
            self.dpi_spin.setRange(1, 2400)
            self.max_file_size_spin = QDoubleSpinBox(self.group)
            self.max_file_size_spin.setRange(0.1, 1000)
            self.max_file_size_spin.setSingleStep(0.1)
            self.resize_mode_combo = QComboBox(self.group)
            for mode in ResizeMode:
                self.resize_mode_combo.addItem("", mode.value)

            self.units_label = QLabel(self.group)
            self.width_label = QLabel(self.group)
            self.height_label = QLabel(self.group)
            self.dpi_label = QLabel(self.group)
            self.resize_mode_label = QLabel(self.group)
            self.max_file_size_label = QLabel(self.group)
            form.addRow(self.units_label, self.units_combo)
            form.addRow(self.width_label, self.width_spin)
            form.addRow(self.height_label, self.height_spin)
            form.addRow(self.dpi_label, self.dpi_spin)
            form.addRow(self.resize_mode_label, self.resize_mode_combo)
            form.addRow(self.max_file_size_label, self.max_file_size_spin)
            layout.addWidget(self.group)
            layout.addStretch(1)

        def retranslate(self, t) -> None:
            self.group.setTitle(t("processing.group"))
            self.units_label.setText(t("processing.units"))
            self.width_label.setText(t("processing.width"))
            self.height_label.setText(t("processing.height"))
            self.dpi_label.setText(t("processing.dpi"))
            self.resize_mode_label.setText(t("processing.resize_mode"))
            self.max_file_size_label.setText(t("processing.max_file_size"))
            self.units_combo.setItemText(0, t("units.pixels"))
            self.units_combo.setItemText(1, t("units.centimeters"))
            for idx, mode in enumerate(ResizeMode):
                self.resize_mode_combo.setItemText(idx, t(f"resize_mode.{mode.value}"))

except ImportError:  # pragma: no cover - depends on environment
    class ProcessingTab:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("PySide6 is required to construct GUI tabs.")
