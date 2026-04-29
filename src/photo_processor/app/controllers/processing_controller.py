from __future__ import annotations

from dataclasses import dataclass

from photo_processor.app.reporting.report_builder import build_processing_report
from photo_processor.app.use_cases.batch_processing import BatchProcessingUseCase
from photo_processor.core.processing_report import ProcessingReport
from photo_processor.core.processing_result import BatchProcessingResult
from photo_processor.core.settings import ProcessingSettings


@dataclass(frozen=True, slots=True)
class ProcessingExecution:
    result: BatchProcessingResult
    report: ProcessingReport


class ProcessingController:
    def run(
        self,
        settings: ProcessingSettings,
        dry_run: bool = False,
        on_progress: callable[[int, int], None] | None = None,
    ) -> ProcessingExecution:
        result = BatchProcessingUseCase(settings).run(dry_run=dry_run, on_progress=on_progress)
        return ProcessingExecution(
            result=result,
            report=build_processing_report(result),
        )
