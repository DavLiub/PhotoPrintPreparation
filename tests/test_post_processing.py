import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.app.use_cases.post_processing import PostProcessingUseCase
from photo_processor.core.cloud_upload import CloudProvider, CloudUploadSettings, UploadResult, UploadStatus
from photo_processor.core.processing_result import BatchProcessingResult
from photo_processor.core.single_image_result import ImageProcessStatus, SingleImageResult


class FakeUploader:
    def __init__(self, failing_names: set[str] | None = None) -> None:
        self.failing_names = failing_names or set()
        self.uploaded_names: list[str] = []

    def upload(self, local_path: Path, settings: CloudUploadSettings) -> UploadResult:
        if local_path.name in self.failing_names:
            raise RuntimeError(f"failed to upload {local_path.name}")
        self.uploaded_names.append(local_path.name)
        remote_path = f"{settings.remote_folder}/{local_path.name}" if settings.remote_folder else local_path.name
        return UploadResult(
            provider=CloudProvider.GOOGLE_DRIVE,
            status=UploadStatus.SUCCESS,
            remote_path=remote_path,
            file_id=f"id-{local_path.stem}",
        )


class PostProcessingUseCaseTestCase(unittest.TestCase):
    def test_uploads_only_successful_items(self) -> None:
        work_dir = Path(self._testMethodName)
        work_dir.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, work_dir)

        uploaded_file = work_dir / "a.jpg"
        uploaded_file.write_bytes(b"a")
        skipped_file = work_dir / "b.jpg"
        skipped_file.write_bytes(b"b")
        result = BatchProcessingResult(found_files=3)
        success_item = SingleImageResult(
            source_path=Path("src/a.jpg"),
            output_path=uploaded_file,
            status=ImageProcessStatus.SUCCESS,
        )
        skipped_item = SingleImageResult(
            source_path=Path("src/b.jpg"),
            output_path=skipped_file,
            status=ImageProcessStatus.SKIPPED,
        )
        error_item = SingleImageResult(
            source_path=Path("src/c.jpg"),
            output_path=work_dir / "c.jpg",
            status=ImageProcessStatus.ERROR,
            error_message="boom",
        )
        result.add_item(success_item)
        result.add_item(skipped_item)
        result.add_item(error_item)

        uploader = FakeUploader()
        settings = CloudUploadSettings(
            enabled=True,
            provider=CloudProvider.GOOGLE_DRIVE,
            remote_folder="folder-1",
        )

        processed = PostProcessingUseCase(settings, uploader).run(result)

        self.assertEqual(uploader.uploaded_names, ["a.jpg"])
        self.assertEqual(processed.uploaded_files, 1)
        self.assertEqual(processed.upload_error_files, 0)
        self.assertEqual(processed.upload_skipped_files, 0)
        self.assertEqual(success_item.upload_result.status, UploadStatus.SUCCESS)
        self.assertEqual(success_item.upload_result.remote_path, "folder-1/a.jpg")
        self.assertIsNone(skipped_item.upload_result)
        self.assertIsNone(error_item.upload_result)

    def test_upload_errors_are_recorded_without_breaking_batch_result(self) -> None:
        work_dir = Path(self._testMethodName)
        work_dir.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, work_dir)

        ok_file = work_dir / "ok.jpg"
        fail_file = work_dir / "fail.jpg"
        ok_file.write_bytes(b"ok")
        fail_file.write_bytes(b"fail")
        result = BatchProcessingResult(found_files=2)
        ok_item = SingleImageResult(source_path=Path("src/ok.jpg"), output_path=ok_file, status=ImageProcessStatus.SUCCESS)
        fail_item = SingleImageResult(source_path=Path("src/fail.jpg"), output_path=fail_file, status=ImageProcessStatus.SUCCESS)
        result.add_item(ok_item)
        result.add_item(fail_item)

        uploader = FakeUploader(failing_names={"fail.jpg"})
        settings = CloudUploadSettings(
            enabled=True,
            provider=CloudProvider.GOOGLE_DRIVE,
            delete_local_after_upload=True,
        )

        processed = PostProcessingUseCase(settings, uploader).run(result)

        self.assertEqual(processed.uploaded_files, 1)
        self.assertEqual(processed.upload_error_files, 1)
        self.assertEqual(processed.upload_skipped_files, 0)
        self.assertFalse(ok_file.exists())
        self.assertTrue(fail_file.exists())
        self.assertEqual(ok_item.upload_result.status, UploadStatus.SUCCESS)
        self.assertEqual(fail_item.upload_result.status, UploadStatus.ERROR)
        self.assertIn("failed to upload", fail_item.upload_result.error_message or "")

    def test_reports_upload_progress_for_upload_candidates(self) -> None:
        work_dir = Path(self._testMethodName)
        work_dir.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, work_dir)

        first_file = work_dir / "a.jpg"
        second_file = work_dir / "b.jpg"
        first_file.write_bytes(b"a")
        second_file.write_bytes(b"b")
        result = BatchProcessingResult(found_files=3)
        result.add_item(
            SingleImageResult(source_path=Path("src/a.jpg"), output_path=first_file, status=ImageProcessStatus.SUCCESS)
        )
        result.add_item(
            SingleImageResult(source_path=Path("src/b.jpg"), output_path=second_file, status=ImageProcessStatus.SUCCESS)
        )
        result.add_item(
            SingleImageResult(source_path=Path("src/c.jpg"), output_path=work_dir / "c.jpg", status=ImageProcessStatus.ERROR)
        )

        progress_updates: list[tuple[int, int]] = []
        PostProcessingUseCase(
            CloudUploadSettings(enabled=True, provider=CloudProvider.GOOGLE_DRIVE),
            FakeUploader(),
        ).run(result, on_progress=lambda current, total: progress_updates.append((current, total)))

        self.assertEqual(progress_updates, [(0, 2), (1, 2), (2, 2)])


def _cleanup_tree(path: Path) -> None:
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_file():
            child.unlink()
        else:
            child.rmdir()
    path.rmdir()
