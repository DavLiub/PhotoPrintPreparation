from __future__ import annotations

from photo_processor.infra.cloud.google_drive_uploader import GoogleDriveFolder, GoogleDriveUploader

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QDialog,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    class GoogleDriveFolderBrowserDialog(QDialog):
        def __init__(
            self,
            uploader: GoogleDriveUploader,
            t,
            initial_folder_id: str | None = None,
            parent: QWidget | None = None,
        ) -> None:
            super().__init__(parent)
            self.uploader = uploader
            self.t = t
            self._selected_folder_id: str | None = None
            self._selected_folder_name: str | None = None
            self._selected_folder_path: str | None = None
            self.current_folder = self._resolve_initial_folder(initial_folder_id)
            self._build_ui()
            self._reload_children()
            self._retranslate()

        def _build_ui(self) -> None:
            self.setModal(True)
            self.resize(620, 460)
            layout = QVBoxLayout(self)

            self.current_folder_label = QLabel(self)
            self.current_folder_label.setWordWrap(True)
            self.current_folder_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

            self.folder_list = QListWidget(self)
            self.folder_list.currentItemChanged.connect(lambda *_args: self._refresh_buttons())
            self.folder_list.itemDoubleClicked.connect(self._open_selected_folder)

            actions_widget = QWidget(self)
            actions_row = QHBoxLayout(actions_widget)
            actions_row.setContentsMargins(0, 0, 0, 0)
            actions_row.setSpacing(8)
            self.up_button = QPushButton(actions_widget)
            self.open_button = QPushButton(actions_widget)
            self.select_button = QPushButton(actions_widget)
            self.cancel_button = QPushButton(actions_widget)
            actions_row.addWidget(self.up_button)
            actions_row.addWidget(self.open_button)
            actions_row.addStretch(1)
            actions_row.addWidget(self.select_button)
            actions_row.addWidget(self.cancel_button)

            self.up_button.clicked.connect(self._go_up)
            self.open_button.clicked.connect(self._open_selected_folder)
            self.select_button.clicked.connect(self._select_current_folder)
            self.cancel_button.clicked.connect(self.reject)

            layout.addWidget(self.current_folder_label)
            layout.addWidget(self.folder_list, 1)
            layout.addWidget(actions_widget)

        def _resolve_initial_folder(self, initial_folder_id: str | None) -> GoogleDriveFolder:
            try:
                return self.uploader.get_folder(initial_folder_id)
            except Exception:
                return self.uploader.get_folder("root")

        def _reload_children(self) -> None:
            self.folder_list.clear()
            for folder in self.uploader.list_folders(self.current_folder.folder_id):
                item = QListWidgetItem(folder.name, self.folder_list)
                item.setData(Qt.UserRole, folder)
            self._refresh_current_folder_label()
            self._refresh_buttons()

        def _refresh_current_folder_label(self) -> None:
            label = self.current_folder.name
            if self.current_folder.folder_id == "root":
                label = self.t("dialog.cloud_browse.current_folder.root")
            self.current_folder_label.setText(
                self.t("dialog.cloud_browse.current_folder").format(
                    name=label,
                    folder_id=self.current_folder.folder_id,
                )
            )

        def _refresh_buttons(self) -> None:
            has_selection = self.folder_list.currentItem() is not None
            self.open_button.setEnabled(has_selection)
            self.up_button.setEnabled(self.current_folder.parent_id is not None)

        def _open_selected_folder(self, item: QListWidgetItem | None = None) -> None:
            current_item = item or self.folder_list.currentItem()
            if current_item is None:
                return
            folder = current_item.data(Qt.UserRole)
            if not isinstance(folder, GoogleDriveFolder):
                return
            self.current_folder = folder
            self._reload_children()

        def _go_up(self) -> None:
            if self.current_folder.parent_id is None:
                return
            self.current_folder = self.uploader.get_folder(self.current_folder.parent_id)
            self._reload_children()

        def _select_current_folder(self) -> None:
            self._selected_folder_id = self.current_folder.folder_id
            self._selected_folder_name = self.current_folder.name
            self._selected_folder_path = self.uploader.get_folder_path(self.current_folder.folder_id)
            self.accept()

        def selected_folder_id(self) -> str | None:
            return self._selected_folder_id

        def selected_folder_name(self) -> str | None:
            return self._selected_folder_name

        def selected_folder_path(self) -> str | None:
            return self._selected_folder_path

        def retranslate(self, t) -> None:
            self.t = t
            self._retranslate()

        def _retranslate(self) -> None:
            self.setWindowTitle(self.t("dialog.cloud_browse.title"))
            self.up_button.setText(self.t("dialog.cloud_browse.up"))
            self.open_button.setText(self.t("dialog.cloud_browse.open"))
            self.select_button.setText(self.t("dialog.cloud_browse.select_current"))
            self.cancel_button.setText(self.t("dialog.cloud_browse.cancel"))
            self._refresh_current_folder_label()
            self._refresh_buttons()

except ImportError:  # pragma: no cover - depends on environment
    class GoogleDriveFolderBrowserDialog:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("PySide6 is required to browse Google Drive folders.")
