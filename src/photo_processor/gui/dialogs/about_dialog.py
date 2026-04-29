from __future__ import annotations

from photo_processor.config.app_info import (
    APP_COPYRIGHT,
    APP_LICENSE_NAME,
    APP_LICENSE_SUMMARY,
    APP_NAME,
    APP_VERSION,
)
from photo_processor.gui.icon_provider import about_icon_path, build_icon

try:
    from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QTextBrowser, QVBoxLayout, QWidget

    class AboutDialog(QDialog):
        def __init__(self, translator, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self.translator = translator
            self._setup_ui()
            self.retranslate()

        def _setup_ui(self) -> None:
            self.resize(720, 540)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(24, 24, 24, 24)
            layout.setSpacing(16)

            self.title_label = QLabel(self)
            self.title_label.setStyleSheet("font-size: 30px; font-weight: 700; color: #0f172a;")
            self.content = QTextBrowser(self)
            self.content.setOpenExternalLinks(True)
            self.content.setStyleSheet(
                "QTextBrowser { background: #ffffff; border: 1px solid #dbe3ee; border-radius: 14px; padding: 20px; font-size: 15px; }"
            )
            self.close_button = QPushButton(self)
            self.close_button.setStyleSheet(
                "QPushButton { min-height: 40px; font-size: 14px; font-weight: 600; padding: 0 18px; "
                "background: #0f172a; color: white; border: none; border-radius: 10px; } "
                "QPushButton:hover { background: #1e293b; }"
            )
            self.close_button.clicked.connect(self.close)

            layout.addWidget(self.title_label)
            layout.addWidget(self.content, 1)
            layout.addWidget(self.close_button)

        def retranslate(self) -> None:
            self.setWindowTitle("About")
            self.setWindowIcon(build_icon(about_icon_path()))
            self.title_label.setText(APP_NAME)
            self.close_button.setText("Close")
            self.content.setHtml(
                f"""
                <html>
                  <body style="font-family: Segoe UI, Arial, sans-serif; font-size: 15px; line-height: 1.65; color: #0f172a; background: #ffffff;">
                    <div style="font-size: 15px; color: #475569; margin-bottom: 18px;">
                      Desktop tool for preparing image batches for print workflows.
                    </div>

                    <div style="margin-bottom: 14px;">
                      <div style="font-size: 14px; font-weight: 700; color: #334155; margin-bottom: 4px;">Version</div>
                      <div>{APP_VERSION}</div>
                    </div>

                    <div style="margin-bottom: 14px;">
                      <div style="font-size: 14px; font-weight: 700; color: #334155; margin-bottom: 4px;">License</div>
                      <div style="font-weight: 700; margin-bottom: 4px;">{APP_LICENSE_NAME}</div>
                      <div>{APP_LICENSE_SUMMARY}</div>
                    </div>

                    <div style="margin-bottom: 18px;">
                      <div style="font-size: 14px; font-weight: 700; color: #334155; margin-bottom: 4px;">Copyright</div>
                      <div>{APP_COPYRIGHT}</div>
                    </div>

                    <div style="font-size: 13px; color: #64748b; padding-top: 10px; border-top: 1px solid #e2e8f0;">
                      Full license terms are provided in <b>LICENSE.md</b> when the application is distributed with that file.
                    </div>
                  </body>
                </html>
                """
            )

except ImportError:  # pragma: no cover - depends on environment
    class AboutDialog:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("PySide6 is required to construct the about dialog.")
