from __future__ import annotations

from photo_processor.infra.cloud.google_drive_uploader import GoogleDriveFolder, GoogleDriveUploader

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QDialog,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QMessageBox,
        QPushButton,
        QTreeWidget,
        QTreeWidgetItem,
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
            self._placeholder_marker = "__placeholder__"
            self._build_ui()
            self._retranslate()
            self._reload_tree()

        def _build_ui(self) -> None:
            self.setModal(True)
            self.resize(700, 520)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(14, 14, 14, 14)
            layout.setSpacing(10)

            self.breadcrumbs_widget = QWidget(self)
            self.breadcrumbs_row = QHBoxLayout(self.breadcrumbs_widget)
            self.breadcrumbs_row.setContentsMargins(0, 0, 0, 0)
            self.breadcrumbs_row.setSpacing(4)

            self.folder_tree = QTreeWidget(self)
            self.folder_tree.setHeaderHidden(True)
            self.folder_tree.setRootIsDecorated(True)
            self.folder_tree.setAlternatingRowColors(True)
            self.folder_tree.currentItemChanged.connect(lambda *_args: self._refresh_buttons())
            self.folder_tree.itemExpanded.connect(self._handle_item_expanded)
            self.folder_tree.itemDoubleClicked.connect(self._open_selected_folder)
            self.folder_tree.setStyleSheet(
                "QTreeWidget { border: 1px solid #e2e8f0; border-radius: 10px; background: #ffffff; }"
            )

            self.empty_state_label = QLabel(self)
            self.empty_state_label.setAlignment(Qt.AlignCenter)
            self.empty_state_label.setWordWrap(True)
            self.empty_state_label.setStyleSheet(
                "QLabel { padding: 18px; border: 1px dashed #cbd5e1; border-radius: 10px; background: #f8fafc; color: #64748b; }"
            )

            actions_widget = QWidget(self)
            actions_row = QHBoxLayout(actions_widget)
            actions_row.setContentsMargins(0, 0, 0, 0)
            actions_row.setSpacing(8)
            self.up_button = QPushButton(actions_widget)
            self.create_button = QPushButton(actions_widget)
            self.open_button = QPushButton(actions_widget)
            self.select_button = QPushButton(actions_widget)
            self.cancel_button = QPushButton(actions_widget)
            actions_row.addWidget(self.up_button)
            actions_row.addWidget(self.create_button)
            actions_row.addWidget(self.open_button)
            actions_row.addStretch(1)
            actions_row.addWidget(self.select_button)
            actions_row.addWidget(self.cancel_button)

            self.up_button.clicked.connect(self._go_up)
            self.create_button.clicked.connect(self._create_folder)
            self.open_button.clicked.connect(self._open_selected_folder)
            self.select_button.clicked.connect(self._select_current_folder)
            self.cancel_button.clicked.connect(self.reject)

            layout.addWidget(self.breadcrumbs_widget)
            layout.addWidget(self.folder_tree, 1)
            layout.addWidget(self.empty_state_label)
            layout.addWidget(actions_widget)

        def _resolve_initial_folder(self, initial_folder_id: str | None) -> GoogleDriveFolder:
            try:
                return self.uploader.get_folder(initial_folder_id)
            except Exception:
                return self.uploader.get_folder("root")

        def _reload_tree(self) -> None:
            self.folder_tree.clear()
            for child_folder in self.uploader.list_folders("root"):
                item = self._build_tree_item(child_folder)
                self.folder_tree.addTopLevelItem(item)
            self._expand_branch_to_current_folder()
            self._refresh_breadcrumbs()
            self._refresh_empty_state()
            self._refresh_buttons()

        def _refresh_breadcrumbs(self) -> None:
            while self.breadcrumbs_row.count():
                item = self.breadcrumbs_row.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.hide()
                    widget.setParent(None)
                    widget.deleteLater()

            chain = self.uploader.get_folder_chain(self.current_folder.folder_id)
            for index, folder in enumerate(chain):
                label = folder.name
                if folder.folder_id == "root":
                    label = self.t("dialog.cloud_browse.current_folder.root")
                is_last = index == len(chain) - 1
                if is_last:
                    current_label = QLabel(label, self.breadcrumbs_widget)
                    current_label.setStyleSheet("QLabel { color: #0f172a; font-weight: 700; padding: 2px 4px; }")
                    self.breadcrumbs_row.addWidget(current_label)
                else:
                    button = QPushButton(label, self.breadcrumbs_widget)
                    button.setFlat(True)
                    button.setStyleSheet(
                        "QPushButton { color: #2563eb; background: transparent; border: none; padding: 2px 4px; text-align: left; }"
                        "QPushButton:hover { text-decoration: underline; }"
                    )
                    button.clicked.connect(lambda _checked=False, target=folder: self._jump_to_folder(target))
                    self.breadcrumbs_row.addWidget(button)
                if index < len(chain) - 1:
                    separator = QLabel("/", self.breadcrumbs_widget)
                    separator.setStyleSheet("color: #94a3b8; padding: 0 2px;")
                    self.breadcrumbs_row.addWidget(separator)
            self.breadcrumbs_row.addStretch(1)

        def _refresh_empty_state(self) -> None:
            current_item = self._find_item_by_folder_id(self.current_folder.folder_id)
            if current_item is None:
                self.empty_state_label.setVisible(self.folder_tree.topLevelItemCount() == 0)
                return
            self._ensure_children_loaded(current_item)
            self.empty_state_label.setVisible(current_item.childCount() == 0)

        def _jump_to_folder(self, folder: GoogleDriveFolder) -> None:
            self.current_folder = folder
            self._reload_tree()

        def _refresh_buttons(self) -> None:
            has_selection = self.folder_tree.currentItem() is not None
            self.open_button.setEnabled(has_selection)
            self.up_button.setEnabled(self.current_folder.parent_id is not None)

        def _build_tree_item(self, folder: GoogleDriveFolder) -> QTreeWidgetItem:
            label = folder.name
            if folder.folder_id == "root":
                label = self.t("dialog.cloud_browse.current_folder.root")
            item = QTreeWidgetItem([label])
            item.setData(0, Qt.UserRole, folder)
            item.setData(0, Qt.UserRole + 1, False)
            item.addChild(QTreeWidgetItem([self._placeholder_marker]))
            return item

        def _ensure_children_loaded(self, item: QTreeWidgetItem) -> None:
            folder = item.data(0, Qt.UserRole)
            if not isinstance(folder, GoogleDriveFolder):
                return
            if item.data(0, Qt.UserRole + 1):
                return
            item.takeChildren()
            for child_folder in self.uploader.list_folders(folder.folder_id):
                item.addChild(self._build_tree_item(child_folder))
            item.setData(0, Qt.UserRole + 1, True)

        def _handle_item_expanded(self, item: QTreeWidgetItem) -> None:
            self._ensure_children_loaded(item)
            self._collapse_siblings(item)

        def _open_selected_folder(self, item: QTreeWidgetItem | None = None, *_args) -> None:
            current_item = item or self.folder_tree.currentItem()
            if current_item is None:
                return
            folder = current_item.data(0, Qt.UserRole)
            if not isinstance(folder, GoogleDriveFolder):
                return
            self.current_folder = folder
            self._reload_tree()

        def _expand_branch_to_current_folder(self) -> None:
            chain = self.uploader.get_folder_chain(self.current_folder.folder_id)
            if len(chain) <= 1:
                first_item = self.folder_tree.topLevelItem(0)
                if first_item is not None:
                    self.folder_tree.setCurrentItem(first_item)
                return

            parent_item: QTreeWidgetItem | None = None
            target_item: QTreeWidgetItem | None = None
            for folder in chain[1:]:
                target_item = self._find_child_item(parent_item, folder.folder_id)
                if target_item is None:
                    break
                self._ensure_children_loaded(target_item)
                self._collapse_siblings(target_item)
                target_item.setExpanded(True)
                parent_item = target_item

            if target_item is not None:
                self.folder_tree.setCurrentItem(target_item)

        def _find_child_item(self, parent_item: QTreeWidgetItem | None, folder_id: str) -> QTreeWidgetItem | None:
            if parent_item is None:
                for index in range(self.folder_tree.topLevelItemCount()):
                    item = self.folder_tree.topLevelItem(index)
                    folder = item.data(0, Qt.UserRole)
                    if isinstance(folder, GoogleDriveFolder) and folder.folder_id == folder_id:
                        return item
                return None

            for index in range(parent_item.childCount()):
                item = parent_item.child(index)
                folder = item.data(0, Qt.UserRole)
                if isinstance(folder, GoogleDriveFolder) and folder.folder_id == folder_id:
                    return item
            return None

        def _find_item_by_folder_id(self, folder_id: str) -> QTreeWidgetItem | None:
            for index in range(self.folder_tree.topLevelItemCount()):
                item = self.folder_tree.topLevelItem(index)
                found = self._find_item_in_subtree(item, folder_id)
                if found is not None:
                    return found
            return None

        def _find_item_in_subtree(self, item: QTreeWidgetItem, folder_id: str) -> QTreeWidgetItem | None:
            folder = item.data(0, Qt.UserRole)
            if isinstance(folder, GoogleDriveFolder) and folder.folder_id == folder_id:
                return item
            for index in range(item.childCount()):
                found = self._find_item_in_subtree(item.child(index), folder_id)
                if found is not None:
                    return found
            return None

        def _collapse_siblings(self, item: QTreeWidgetItem) -> None:
            parent_item = item.parent()
            if parent_item is None:
                for index in range(self.folder_tree.topLevelItemCount()):
                    sibling = self.folder_tree.topLevelItem(index)
                    if sibling is not item:
                        sibling.setExpanded(False)
                return

            for index in range(parent_item.childCount()):
                sibling = parent_item.child(index)
                if sibling is not item:
                    sibling.setExpanded(False)

        def _go_up(self) -> None:
            if self.current_folder.parent_id is None:
                return
            self.current_folder = self.uploader.get_folder(self.current_folder.parent_id)
            self._reload_tree()

        def _create_folder(self) -> None:
            folder_name, accepted = QInputDialog.getText(
                self,
                self.t("dialog.cloud_browse.create.title"),
                self.t("dialog.cloud_browse.create.prompt"),
            )
            if not accepted:
                return
            folder_name = folder_name.strip()
            if not folder_name:
                QMessageBox.warning(
                    self,
                    self.t("dialog.cloud_browse.create.title"),
                    self.t("dialog.cloud_browse.create.empty_name"),
                )
                return
            try:
                created_folder = self.uploader.create_folder(folder_name, self.current_folder.folder_id)
            except Exception as exc:
                QMessageBox.critical(
                    self,
                    self.t("dialog.cloud_browse.create.failed.title"),
                    str(exc),
                )
                return
            self.current_folder = created_folder
            self._reload_tree()

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
            self.create_button.setText(self.t("dialog.cloud_browse.create"))
            self.open_button.setText(self.t("dialog.cloud_browse.open"))
            self.select_button.setText(self.t("dialog.cloud_browse.select_current"))
            self.cancel_button.setText(self.t("dialog.cloud_browse.cancel"))
            self.empty_state_label.setText(self.t("dialog.cloud_browse.empty"))
            self._refresh_breadcrumbs()
            self._refresh_buttons()

except ImportError:  # pragma: no cover - depends on environment
    class GoogleDriveFolderBrowserDialog:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("PySide6 is required to browse Google Drive folders.")
