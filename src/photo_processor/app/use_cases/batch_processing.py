from __future__ import annotations

from photo_processor.core.image_task import ImageTask
from photo_processor.core.output_policy import ConflictStrategy
from photo_processor.core.processing_result import BatchProcessingResult
from photo_processor.core.settings import ProcessingSettings
from photo_processor.core.single_image_result import ImageProcessStatus, SingleImageResult
from photo_processor.infra.filesystem.file_scanner import scan_supported_images
from photo_processor.infra.filesystem.output_path_builder import build_output_path
from photo_processor.infra.imaging.image_processor import ImageProcessor


class BatchProcessingUseCase:
    def __init__(self, settings: ProcessingSettings) -> None:
        self.settings = settings
        self.image_processor = ImageProcessor(settings)

    def run(
        self,
        dry_run: bool = False,
        on_progress: callable[[int, int], None] | None = None,
    ) -> BatchProcessingResult:
        result = BatchProcessingResult()
        files = scan_supported_images(self.settings.source_folder, self.settings.source_formats)
        result.found_files = len(files)
        if on_progress is not None:
            on_progress(0, result.found_files)

        if not self.settings.source_folder.exists():
            result.add_item(
                SingleImageResult(
                    source_path=self.settings.source_folder,
                    output_path=self.settings.output_folder,
                    status=ImageProcessStatus.ERROR,
                    error_message=f"Source folder does not exist: {self.settings.source_folder}",
                )
            )
            if on_progress is not None:
                on_progress(0, result.found_files)
            return result

        self.settings.output_folder.mkdir(parents=True, exist_ok=True)

        for source_path in files:
            output_path = build_output_path(
                source_path=source_path,
                output_folder=self.settings.output_folder,
                policy=self.settings.output_policy,
            )
            if output_path is None:
                result.add_item(
                    SingleImageResult(
                        source_path=source_path,
                        output_path=self.settings.output_folder / f"{source_path.stem}{self.settings.output_policy.filename_suffix}{self.settings.output_policy.output_format.extension}",
                        status=ImageProcessStatus.SKIPPED,
                        warnings=["Skipped because the target output file already exists."],
                    )
                )
                if on_progress is not None:
                    on_progress(len(result.items), result.found_files)
                continue
            task = ImageTask(source_path=source_path, output_path=output_path)

            if dry_run:
                result.add_item(
                    SingleImageResult(
                        source_path=source_path,
                        output_path=output_path,
                        status=ImageProcessStatus.SUCCESS,
                        warnings=["Dry run: output file was not written."],
                    )
                )
                if on_progress is not None:
                    on_progress(len(result.items), result.found_files)
                continue

            try:
                item = self.image_processor.process(task)
            except Exception as exc:  # pragma: no cover - defensive reporting
                item = SingleImageResult(
                    source_path=source_path,
                    output_path=output_path,
                    status=ImageProcessStatus.ERROR,
                    error_message=str(exc),
                )
            result.add_item(item)
            if on_progress is not None:
                on_progress(len(result.items), result.found_files)

        return result
