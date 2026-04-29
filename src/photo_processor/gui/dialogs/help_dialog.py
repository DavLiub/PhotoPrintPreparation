from __future__ import annotations

try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QTextCursor
    from PySide6.QtWidgets import (
        QDialog,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QSplitter,
        QTextBrowser,
        QVBoxLayout,
        QWidget,
    )

    class HelpDialog(QDialog):
        def __init__(self, translator, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self.translator = translator
            self.section_keys = [
                ("help.nav.overview", "overview"),
                ("help.section.setup", "setup"),
                ("help.section.processing", "processing"),
                ("help.section.actions", "actions"),
                ("help.section.report", "report"),
            ]
            self._setup_ui()
            self.retranslate()

        def _setup_ui(self) -> None:
            self.resize(980, 760)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(18, 18, 18, 18)
            layout.setSpacing(12)

            self.title_label = QLabel(self)
            self.title_label.setStyleSheet("font-size: 28px; font-weight: 700; color: #0f172a;")
            self.subtitle_label = QLabel(self)
            self.subtitle_label.setWordWrap(True)
            self.subtitle_label.setStyleSheet("font-size: 15px; color: #475569;")

            search_row = QHBoxLayout()
            search_row.setSpacing(8)
            self.search_label = QLabel(self)
            self.search_edit = QLineEdit(self)
            self.search_next_button = QPushButton(self)
            self.search_close_button = QPushButton(self)
            self.search_status_label = QLabel(self)
            self.search_edit.returnPressed.connect(self.find_next)
            self.search_next_button.clicked.connect(self.find_next)
            self.search_close_button.clicked.connect(self.close)
            search_row.addWidget(self.search_label)
            search_row.addWidget(self.search_edit, 1)
            search_row.addWidget(self.search_next_button)
            search_row.addWidget(self.search_close_button)

            self.sections_list = QListWidget(self)
            self.sections_list.setMinimumWidth(220)
            self.sections_list.currentRowChanged.connect(self._show_section)
            self.sections_list.setStyleSheet(
                "QListWidget { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px; font-size: 15px; }"
                "QListWidget::item { padding: 12px 14px; border-radius: 8px; }"
                "QListWidget::item:selected { background: #dbeafe; color: #1d4ed8; font-weight: 600; }"
            )

            self.browser = QTextBrowser(self)
            self.browser.setOpenExternalLinks(True)
            self.browser.setStyleSheet(
                "QTextBrowser { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px; font-size: 15px; }"
            )
            self.browser.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            splitter = QSplitter(self)
            splitter.addWidget(self.sections_list)
            splitter.addWidget(self.browser)
            splitter.setStretchFactor(0, 0)
            splitter.setStretchFactor(1, 1)

            layout.addWidget(self.title_label)
            layout.addWidget(self.subtitle_label)
            layout.addLayout(search_row)
            layout.addWidget(self.search_status_label)
            layout.addWidget(splitter, 1)

        def retranslate(self) -> None:
            t = self.translator.text
            self.setWindowTitle(t("help.title"))
            self.title_label.setText(t("help.title"))
            self.subtitle_label.setText(t("help.overview"))
            self.search_label.setText(t("help.search.label"))
            self.search_edit.setPlaceholderText(t("help.search.placeholder"))
            self.search_next_button.setText(t("help.search.next"))
            self.search_close_button.setText(t("help.search.close"))
            self.search_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #334155;")
            self.search_edit.setStyleSheet("min-height: 36px; font-size: 14px; padding: 0 10px;")
            self.search_next_button.setStyleSheet("min-height: 36px; font-size: 14px; padding: 0 14px;")
            self.search_close_button.setStyleSheet("min-height: 36px; font-size: 14px; padding: 0 14px;")
            self.search_status_label.setStyleSheet("font-size: 13px; color: #64748b;")
            self.search_status_label.setText("")
            self.browser.setHtml(self._build_help_html())
            self.sections_list.clear()
            for key, _anchor in self.section_keys:
                QListWidgetItem(t(key), self.sections_list)
            if self.sections_list.count() > 0 and self.sections_list.currentRow() < 0:
                self.sections_list.setCurrentRow(0)

        def find_next(self) -> None:
            query = self.search_edit.text().strip()
            if not query:
                self.search_status_label.setText("")
                return
            if self.browser.find(query):
                self.search_status_label.setText("")
                return

            cursor = self.browser.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self.browser.setTextCursor(cursor)
            if self.browser.find(query):
                self.search_status_label.setText(self.translator.text("help.search.wrapped"))
                return

            self.search_status_label.setText(self.translator.text("help.search.no_matches"))

        def _show_section(self, index: int) -> None:
            if index < 0 or index >= len(self.section_keys):
                return
            _label_key, anchor = self.section_keys[index]
            self.browser.scrollToAnchor(anchor)

        def _build_help_html(self) -> str:
            t = self.translator.text
            return f"""
            <html>
              <body style="font-family: Segoe UI, Arial, sans-serif; font-size: 15px; line-height: 1.65; color: #0f172a;">
                <a name="overview"></a>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:16px 18px; margin-bottom:18px;">
                  <h2 style="font-size:24px; margin:0 0 8px 0;">{t("help.nav.overview")}</h2>
                  <p style="margin:0;">{t("help.overview")}</p>
                </div>

                <a name="setup"></a>
                <h2 style="font-size:24px; margin:18px 0 8px 0;">{t("help.section.setup")}</h2>
                <ul>
                  <li><b>{t("source.folder")}:</b> {t("help.desc.source_folder")}</li>
                  <li><b>{t("source.preset")}:</b> {t("help.desc.preset")}</li>
                  <li><b>{t("source.formats")}:</b> {t("help.desc.source_formats")}</li>
                  <li><b>{t("output.folder")}:</b> {t("help.desc.output_folder")}</li>
                  <li><b>{t("output.suffix")}:</b> {t("help.desc.filename_suffix")}</li>
                  <li><b>{t("output.extension")}:</b> {t("help.desc.output_extension")}</li>
                  <li><b>{t("output.conflict_strategy")}:</b> {t("help.desc.conflict_strategy")}</li>
                </ul>

                <a name="processing"></a>
                <h2 style="font-size:24px; margin:18px 0 8px 0;">{t("help.section.processing")}</h2>
                <ul>
                  <li><b>{t("processing.units")}:</b> {t("help.desc.units")}</li>
                  <li><b>{t("processing.width")}:</b> {t("help.desc.width")}</li>
                  <li><b>{t("processing.height")}:</b> {t("help.desc.height")}</li>
                  <li><b>{t("processing.dpi")}:</b> {t("help.desc.dpi")} <a href="https://en.wikipedia.org/wiki/Dots_per_inch">Wikipedia</a></li>
                  <li><b>{t("processing.resize_mode")}:</b> {t("help.desc.resize_mode")}</li>
                  <li><b>{t("processing.max_file_size")}:</b> {t("help.desc.max_file_size")}</li>
                </ul>

                <a name="actions"></a>
                <h2 style="font-size:24px; margin:18px 0 8px 0;">{t("help.section.actions")}</h2>
                <ul>
                  <li><b>{t("actions.preview")}:</b> {t("help.desc.preview")}</li>
                  <li><b>{t("actions.start")}:</b> {t("help.desc.start")}</li>
                  <li><b>{t("help.progress")}:</b> {t("help.desc.progress")}</li>
                  <li><b>{t("actions.open_output")}:</b> {t("help.desc.open_output")}</li>
                  <li><b>{t("actions.save_settings")}:</b> {t("help.desc.save_settings")}</li>
                </ul>

                <a name="report"></a>
                <h2 style="font-size:24px; margin:18px 0 8px 0;">{t("help.section.report")}</h2>
                <ul>
                  <li><b>{t("report.summary")}:</b> {t("help.desc.report_summary")}</li>
                  <li><b>{t("report.warnings")}:</b> {t("help.desc.report_warnings")}</li>
                </ul>
              </body>
            </html>
            """

except ImportError:  # pragma: no cover - depends on environment
    class HelpDialog:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("PySide6 is required to construct the help dialog.")
