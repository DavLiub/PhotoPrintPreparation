from __future__ import annotations

from photo_processor.app.use_cases.connect_google_drive import ConnectGoogleDriveUseCase

try:
    from PySide6.QtCore import QObject, Signal, Slot

    class GoogleDriveConnectWorker(QObject):
        finished = Signal(object)
        failed = Signal(str)

        def __init__(self, use_case: ConnectGoogleDriveUseCase) -> None:
            super().__init__()
            self.use_case = use_case

        @Slot()
        def run(self) -> None:
            try:
                connection = self.use_case.run()
            except Exception as exc:  # pragma: no cover - GUI boundary
                self.failed.emit(str(exc))
                return
            self.finished.emit(connection)

except ImportError:  # pragma: no cover - depends on environment
    class GoogleDriveConnectWorker:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("PySide6 is required to construct the Google Drive connect worker.")
