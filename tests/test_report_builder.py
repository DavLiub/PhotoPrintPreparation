import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from photo_processor.app.reporting.report_builder import build_processing_report
from photo_processor.core.cloud_upload import CloudProvider, UploadResult, UploadStatus
from photo_processor.core.processing_result import BatchProcessingResult
from photo_processor.core.single_image_result import ImageProcessStatus, SingleImageResult


class ReportBuilderTestCase(unittest.TestCase):
    def test_build_processing_report_aggregates_warning_count(self) -> None:
        result = BatchProcessingResult(found_files=3)
        result.add_item(
            SingleImageResult(
                source_path=Path("a.jpg"),
                output_path=Path("out/a.jpg"),
                status=ImageProcessStatus.SUCCESS,
                warnings=["w1", "w2"],
            )
        )
        result.add_item(
            SingleImageResult(
                source_path=Path("b.jpg"),
                output_path=Path("out/b.jpg"),
                status=ImageProcessStatus.SKIPPED,
                warnings=["w3"],
            )
        )
        result.add_item(
            SingleImageResult(
                source_path=Path("c.jpg"),
                output_path=Path("out/c.jpg"),
                status=ImageProcessStatus.ERROR,
                error_message="boom",
            )
        )
        result.add_upload_result(
            result.items[0],
            UploadResult(
                provider=CloudProvider.GOOGLE_DRIVE,
                status=UploadStatus.SUCCESS,
                remote_path="folder/a.jpg",
            ),
        )
        result.add_upload_result(
            result.items[1],
            UploadResult(
                provider=CloudProvider.GOOGLE_DRIVE,
                status=UploadStatus.SKIPPED,
                error_message="already exists",
            ),
        )

        report = build_processing_report(result)

        self.assertEqual(report.found_files, 3)
        self.assertEqual(report.processed_files, 1)
        self.assertEqual(report.skipped_files, 1)
        self.assertEqual(report.error_files, 1)
        self.assertEqual(report.uploaded_files, 1)
        self.assertEqual(report.upload_skipped_files, 1)
        self.assertEqual(report.upload_error_files, 0)
        self.assertEqual(report.warning_count, 3)
        self.assertIn("Uploaded: 1", report.summary_lines)
        self.assertIn("Upload skipped: 1", report.summary_lines)
        self.assertIn("Warnings: 3", report.summary_lines)
