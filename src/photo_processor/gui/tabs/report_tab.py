from __future__ import annotations

try:
    from PySide6.QtWidgets import QGroupBox, QTextEdit, QVBoxLayout, QWidget

    class ReportTab(QWidget):
        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            layout = QVBoxLayout(self)
            self.group = QGroupBox(self)
            group_layout = QVBoxLayout(self.group)
            self.report_placeholder = QTextEdit(self.group)
            self.report_placeholder.setReadOnly(True)
            group_layout.addWidget(self.report_placeholder)
            layout.addWidget(self.group)

        def retranslate(self, t) -> None:
            self.group.setTitle(t("report.group"))
            if not self.report_placeholder.toPlainText():
                self.report_placeholder.setPlainText(t("report.placeholder"))

        def set_report_text(self, text: str) -> None:
            self.report_placeholder.setPlainText(text)

        def clear_report(self) -> None:
            self.report_placeholder.clear()

except ImportError:  # pragma: no cover - depends on environment
    class ReportTab:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("PySide6 is required to construct GUI tabs.")
