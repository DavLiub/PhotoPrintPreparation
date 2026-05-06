import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.app.controllers.processing_controller import ProcessingController
from photo_processor.core.cloud_upload import CloudProvider, CloudUploadSettings, UploadResult, UploadStatus
from photo_processor.core.settings import ProcessingSettings
from photo_processor.core.single_image_result import ImageProcessStatus, SingleImageResult


class FakeUploader:
    def upload(self, local_path: Path, _settings: CloudUploadSettings) -> UploadResult:
        return UploadResult(
            provider=CloudProvider.GOOGLE_DRIVE,
            status=UploadStatus.SUCCESS,
            remote_path=f"folder/{local_path.name}",
        )


class ProcessingControllerTestCase(unittest.TestCase):
    def test_run_returns_result_and_report(self) -> None:
        source_dir = Path(self._testMethodName)
        output_dir = source_dir / "out"
        source_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, source_dir)

        (source_dir / "a.jpg").write_bytes(b"jpg")
        (source_dir / "b.png").write_bytes(b"png")

        execution = ProcessingController().run(
            ProcessingSettings(source_folder=source_dir, output_folder=output_dir),
            dry_run=True,
        )

        self.assertEqual(execution.result.found_files, 2)
        self.assertEqual(execution.report.found_files, 2)
        self.assertEqual(execution.report.processed_files, 2)
        self.assertTrue(any("Found files" in line for line in execution.report.summary_lines))

    def test_run_applies_post_processing_when_cloud_upload_is_enabled(self) -> None:
        source_dir = Path(self._testMethodName)
        output_dir = source_dir / "out"
        source_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, source_dir)

        source_file = source_dir / "a.jpg"
        source_file.write_bytes(b"jpg")

        settings = ProcessingSettings(
            source_folder=source_dir,
            output_folder=output_dir,
            cloud_upload=CloudUploadSettings(
                enabled=True,
                provider=CloudProvider.GOOGLE_DRIVE,
                remote_folder="folder",
            ),
        )

        def fake_process(task) -> SingleImageResult:
            task.output_path.write_bytes(b"processed")
            return SingleImageResult(
                source_path=task.source_path,
                output_path=task.output_path,
                status=ImageProcessStatus.SUCCESS,
            )

        with patch("photo_processor.app.use_cases.batch_processing.ImageProcessor.process", side_effect=fake_process):
            execution = ProcessingController(
                cloud_uploader_factory=lambda _settings: FakeUploader()
            ).run(settings)

        self.assertEqual(execution.report.processed_files, 1)
        self.assertEqual(execution.report.uploaded_files, 1)
        self.assertEqual(execution.report.upload_error_files, 0)
        self.assertEqual(execution.result.items[0].upload_result.status, UploadStatus.SUCCESS)

    def test_run_reports_upload_progress_when_cloud_upload_is_enabled(self) -> None:
        source_dir = Path(self._testMethodName)
        output_dir = source_dir / "out"
        source_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        self.addCleanup(_cleanup_tree, source_dir)

        source_file = source_dir / "a.jpg"
        source_file.write_bytes(b"jpg")

        settings = ProcessingSettings(
            source_folder=source_dir,
            output_folder=output_dir,
            cloud_upload=CloudUploadSettings(
                enabled=True,
                provider=CloudProvider.GOOGLE_DRIVE,
                remote_folder="folder",
            ),
        )
        upload_progress: list[tuple[int, int]] = []

        def fake_process(task) -> SingleImageResult:
            task.output_path.write_bytes(b"processed")
            return SingleImageResult(
                source_path=task.source_path,
                output_path=task.output_path,
                status=ImageProcessStatus.SUCCESS,
            )

        with patch("photo_processor.app.use_cases.batch_processing.ImageProcessor.process", side_effect=fake_process):
            ProcessingController(
                cloud_uploader_factory=lambda _settings: FakeUploader()
            ).run(
                settings,
                on_upload_progress=lambda current, total: upload_progress.append((current, total)),
            )

        self.assertEqual(upload_progress, [(0, 1), (1, 1)])


def _cleanup_tree(path: Path) -> None:
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_file():
            child.unlink()
        else:
            child.rmdir()
    path.rmdir()
