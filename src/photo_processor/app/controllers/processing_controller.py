from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from photo_processor.app.reporting.report_builder import build_processing_report
from photo_processor.app.use_cases.post_processing import PostProcessingUseCase
from photo_processor.app.use_cases.batch_processing import BatchProcessingUseCase
from photo_processor.app.ports.cloud_uploader import CloudUploader
from photo_processor.core.processing_report import ProcessingReport
from photo_processor.core.processing_result import BatchProcessingResult
from photo_processor.core.settings import ProcessingSettings


@dataclass(frozen=True, slots=True)
class ProcessingExecution:
    result: BatchProcessingResult
    report: ProcessingReport


class ProcessingController:
    def __init__(
        self,
        cloud_uploader_factory: Callable[[ProcessingSettings], CloudUploader] | None = None,
    ) -> None:
        self.cloud_uploader_factory = cloud_uploader_factory

    def run(
        self,
        settings: ProcessingSettings,
        dry_run: bool = False,
        on_progress: callable[[int, int], None] | None = None,
    ) -> ProcessingExecution:
        result = BatchProcessingUseCase(settings).run(dry_run=dry_run, on_progress=on_progress)
        if not dry_run and settings.cloud_upload.is_enabled:
            if self.cloud_uploader_factory is None:
                raise RuntimeError("Cloud upload is enabled but no cloud uploader factory is configured.")
            uploader = self.cloud_uploader_factory(settings)
            result = PostProcessingUseCase(settings.cloud_upload, uploader).run(result)
        return ProcessingExecution(
            result=result,
            report=build_processing_report(result),
        )
