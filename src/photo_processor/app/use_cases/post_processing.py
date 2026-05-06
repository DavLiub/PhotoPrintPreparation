from __future__ import annotations

from photo_processor.app.ports.cloud_uploader import CloudUploader
from photo_processor.core.cloud_upload import CloudUploadSettings, UploadResult, UploadStatus
from photo_processor.core.processing_result import BatchProcessingResult
from photo_processor.core.single_image_result import SingleImageResult


class PostProcessingUseCase:
    def __init__(self, settings: CloudUploadSettings, uploader: CloudUploader) -> None:
        self.settings = settings
        self.uploader = uploader

    def run(self, result: BatchProcessingResult) -> BatchProcessingResult:
        for item in result.items:
            self._process_item(result, item)
        return result

    def _process_item(self, result: BatchProcessingResult, item: SingleImageResult) -> None:
        if not item.success:
            return
        if not item.output_path.exists():
            result.add_upload_result(
                item,
                UploadResult(
                    provider=self.settings.provider or self._default_provider(),
                    status=UploadStatus.SKIPPED,
                    error_message="Output file is missing, so upload was skipped.",
                ),
            )
            return

        try:
            upload_result = self.uploader.upload(item.output_path, self.settings)
        except Exception as exc:  # pragma: no cover - defensive boundary
            upload_result = UploadResult(
                provider=self.settings.provider or self._default_provider(),
                status=UploadStatus.ERROR,
                error_message=str(exc),
            )

        result.add_upload_result(item, upload_result)

        if (
            upload_result.status is UploadStatus.SUCCESS
            and self.settings.delete_local_after_upload
            and item.output_path.exists()
        ):
            item.output_path.unlink()

    def _default_provider(self):
        from photo_processor.core.cloud_upload import CloudProvider

        return CloudProvider.GOOGLE_DRIVE
