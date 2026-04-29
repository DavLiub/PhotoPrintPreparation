from __future__ import annotations

from photo_processor.core.image_task import ImageTask
from photo_processor.core.processing_result import BatchProcessingResult
from photo_processor.core.settings import ProcessingSettings
from photo_processor.infra.filesystem.file_scanner import scan_supported_images
from photo_processor.infra.filesystem.output_path_builder import build_output_path
from photo_processor.infra.imaging.image_processor import ImageProcessor


class BatchProcessingUseCase:
    def __init__(self, settings: ProcessingSettings) -> None:
        self.settings = settings
        self.image_processor = ImageProcessor(settings)

    def run(self, dry_run: bool = False) -> BatchProcessingResult:
        result = BatchProcessingResult()
        files = scan_supported_images(self.settings.source_folder, self.settings.source_formats)
        result.found_files = len(files)

        if not self.settings.source_folder.exists():
            result.error_files = 1
            result.messages.append(f"Source folder does not exist: {self.settings.source_folder}")
            return result

        self.settings.output_folder.mkdir(parents=True, exist_ok=True)

        for source_path in files:
            output_path = build_output_path(
                source_path=source_path,
                output_folder=self.settings.output_folder,
                suffix=self.settings.filename_suffix,
                extension=".jpg",
            )
            task = ImageTask(source_path=source_path, output_path=output_path)

            if dry_run:
                result.processed_files += 1
                result.messages.append(f"DRY RUN {source_path} -> {output_path}")
                continue

            try:
                self.image_processor.process(task)
            except NotImplementedError as exc:
                result.error_files += 1
                result.messages.append(str(exc))
                break
            except Exception as exc:  # pragma: no cover - defensive reporting
                result.error_files += 1
                result.messages.append(f"ERROR {source_path}: {exc}")
            else:
                result.processed_files += 1

        return result
