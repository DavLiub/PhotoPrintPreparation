from __future__ import annotations

from photo_processor.app.controllers.processing_controller import ProcessingController
from photo_processor.core.settings import ProcessingSettings

try:
    from PySide6.QtCore import QObject, Signal, Slot

    class ProcessingWorker(QObject):
        finished = Signal(object)
        failed = Signal(str)
        progress = Signal(int, int)
        upload_progress = Signal(int, int)

        def __init__(
            self,
            processing_controller: ProcessingController,
            settings: ProcessingSettings,
            dry_run: bool,
        ) -> None:
            super().__init__()
            self.processing_controller = processing_controller
            self.settings = settings
            self.dry_run = dry_run

        @Slot()
        def run(self) -> None:
            try:
                execution = self.processing_controller.run(
                    self.settings,
                    dry_run=self.dry_run,
                    on_progress=self._emit_progress,
                    on_upload_progress=self._emit_upload_progress,
                )
            except Exception as exc:  # pragma: no cover - defensive GUI boundary
                self.failed.emit(str(exc))
                return
            self.finished.emit(execution)

        def _emit_progress(self, current: int, total: int) -> None:
            self.progress.emit(current, total)

        def _emit_upload_progress(self, current: int, total: int) -> None:
            self.upload_progress.emit(current, total)

except ImportError:  # pragma: no cover - depends on environment
    class ProcessingWorker:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("PySide6 is required to construct the GUI worker.")
