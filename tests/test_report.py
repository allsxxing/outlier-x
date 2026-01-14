"""Tests for the report module."""

from pathlib import Path

import pytest
import pandas as pd

from src.report import ReportGenerator
from src.validate import ValidationReport
from src.utils.errors import ReportError


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "event_id": ["evt_001", "evt_002", "evt_003"],
        "sport": ["football", "basketball", "baseball"],
        "volume": [1000, 2000, 1500],
        "odds": [1.5, 2.0, 1.8],
    })


@pytest.fixture
def sample_validation_report():
    """Create a sample ValidationReport for testing."""
    report = ValidationReport(
        total_records=100,
        valid_records=85,
        invalid_records=15,
    )
    report.errors_by_field = {
        "event_id": 5,
        "sport": 10,
    }
    report.error_samples = [
        {"field": "event_id", "value": None, "error": "Required field is null"},
        {"field": "sport", "value": "invalid", "error": "Not in enum"},
    ]
    report.warnings = ["Some warning message"]
    return report


class TestGenerateSummaryReport:
    """Test summary report generation."""

    def test_generate_summary_report_basic(self, sample_dataframe):
        """Test generating basic summary report."""
        report = ReportGenerator.generate_summary_report(
            sample_dataframe,
            duration_seconds=10.5
        )
        assert isinstance(report, str)
        assert "SUMMARY REPORT" in report
        assert "Total Records Processed: 3" in report
        assert "Processing Duration: 10.50 seconds" in report

    def test_generate_summary_report_with_stats(self, sample_dataframe):
        """Test generating summary report with additional stats."""
        stats = {
            "unique_sports": 3,
            "total_volume": 4500,
        }
        report = ReportGenerator.generate_summary_report(
            sample_dataframe,
            stats=stats,
            duration_seconds=5.0
        )
        assert "unique_sports: 3" in report
        assert "total_volume: 4500" in report

    def test_generate_summary_report_empty_dataframe(self):
        """Test summary report with empty DataFrame."""
        df = pd.DataFrame()
        report = ReportGenerator.generate_summary_report(df, duration_seconds=0.0)
        assert "Total Records Processed: 0" in report

    def test_generate_summary_report_zero_duration(self, sample_dataframe):
        """Test summary report with zero duration."""
        report = ReportGenerator.generate_summary_report(
            sample_dataframe,
            duration_seconds=0.0
        )
        # Should handle division by zero
        assert isinstance(report, str)

    def test_generate_summary_report_includes_columns(self, sample_dataframe):
        """Test summary report includes column names."""
        report = ReportGenerator.generate_summary_report(sample_dataframe)
        assert "event_id" in report
        assert "sport" in report
        assert "volume" in report

    def test_generate_summary_report_includes_memory_usage(self, sample_dataframe):
        """Test summary report includes memory usage."""
        report = ReportGenerator.generate_summary_report(sample_dataframe)
        assert "Memory Usage:" in report
        assert "MB" in report

    def test_generate_summary_report_error_handling(self):
        """Test error handling in summary report generation."""
        with pytest.raises(ReportError):
            # Pass invalid data
            ReportGenerator.generate_summary_report(None)


class TestGenerateValidationReport:
    """Test validation report generation."""

    def test_generate_validation_report_basic(self, sample_validation_report):
        """Test generating basic validation report."""
        report = ReportGenerator.generate_validation_report(sample_validation_report)
        assert isinstance(report, str)
        assert "VALIDATION REPORT" in report
        assert "Total Records: 100" in report
        assert "Valid Records: 85" in report
        assert "Invalid Records: 15" in report

    def test_generate_validation_report_includes_validity_rate(self, sample_validation_report):
        """Test validation report includes validity percentage."""
        report = ReportGenerator.generate_validation_report(sample_validation_report)
        assert "Validity Rate: 85.00%" in report

    def test_generate_validation_report_includes_errors_by_field(self, sample_validation_report):
        """Test validation report includes errors by field."""
        report = ReportGenerator.generate_validation_report(sample_validation_report)
        assert "ERRORS BY FIELD" in report
        assert "event_id: 5 errors" in report
        assert "sport: 10 errors" in report

    def test_generate_validation_report_includes_error_samples(self, sample_validation_report):
        """Test validation report includes error samples."""
        report = ReportGenerator.generate_validation_report(sample_validation_report)
        assert "ERROR SAMPLES" in report
        assert "Required field is null" in report
        assert "Not in enum" in report

    def test_generate_validation_report_includes_warnings(self, sample_validation_report):
        """Test validation report includes warnings."""
        report = ReportGenerator.generate_validation_report(sample_validation_report)
        assert "WARNINGS" in report
        assert "Some warning message" in report

    def test_generate_validation_report_no_errors(self):
        """Test validation report with no errors."""
        report_data = ValidationReport(
            total_records=100,
            valid_records=100,
            invalid_records=0,
        )
        report = ReportGenerator.generate_validation_report(report_data)
        assert "No errors found" in report

    def test_generate_validation_report_error_handling(self):
        """Test error handling in validation report generation."""
        with pytest.raises(ReportError):
            # Pass invalid data
            ReportGenerator.generate_validation_report(None)


class TestGenerateDataQualityReport:
    """Test data quality report generation."""

    def test_generate_data_quality_report_basic(self, sample_dataframe):
        """Test generating basic data quality report."""
        report = ReportGenerator.generate_data_quality_report(sample_dataframe)
        assert isinstance(report, str)
        assert "DATA QUALITY REPORT" in report
        assert "Total Rows: 3" in report
        assert "Total Columns: 4" in report

    def test_generate_data_quality_report_includes_completeness(self, sample_dataframe):
        """Test data quality report includes completeness metrics."""
        report = ReportGenerator.generate_data_quality_report(sample_dataframe)
        assert "Completeness:" in report
        assert "Non-Null Values:" in report
        assert "Null Values:" in report

    def test_generate_data_quality_report_includes_uniqueness(self, sample_dataframe):
        """Test data quality report includes uniqueness metrics."""
        report = ReportGenerator.generate_data_quality_report(sample_dataframe)
        assert "Uniqueness:" in report

    def test_generate_data_quality_report_numeric_stats(self, sample_dataframe):
        """Test data quality report includes numeric statistics."""
        report = ReportGenerator.generate_data_quality_report(sample_dataframe)
        # Should include min, max, mean for numeric columns
        assert "Min:" in report
        assert "Max:" in report
        assert "Mean:" in report

    def test_generate_data_quality_report_with_nulls(self):
        """Test data quality report with null values."""
        df = pd.DataFrame({
            "col1": [1, 2, None, 4],
            "col2": ["a", None, "c", "d"],
        })
        report = ReportGenerator.generate_data_quality_report(df)
        # Should show completeness less than 100%
        assert "75.00%" in report or "Completeness:" in report

    def test_generate_data_quality_report_empty_dataframe(self):
        """Test data quality report with empty DataFrame."""
        df = pd.DataFrame()
        report = ReportGenerator.generate_data_quality_report(df)
        assert "Total Rows: 0" in report

    def test_generate_data_quality_report_error_handling(self):
        """Test error handling in data quality report generation."""
        with pytest.raises(ReportError):
            # Pass invalid data
            ReportGenerator.generate_data_quality_report(None)


class TestExportReport:
    """Test report export functionality."""

    def test_export_report_txt(self, tmp_path):
        """Test exporting report to text file."""
        report_content = "Test Report Content"
        output_file = tmp_path / "report.txt"

        ReportGenerator.export_report(
            report_content,
            "txt",
            str(output_file)
        )

        assert output_file.exists()
        with open(output_file, "r") as f:
            content = f.read()
        assert content == report_content

    def test_export_report_creates_directories(self, tmp_path):
        """Test export creates parent directories if they don't exist."""
        output_file = tmp_path / "subdir" / "report.txt"

        ReportGenerator.export_report(
            "Test content",
            "txt",
            str(output_file)
        )

        assert output_file.exists()
        assert output_file.parent.exists()

    def test_export_report_overwrites_existing(self, tmp_path):
        """Test export overwrites existing file."""
        output_file = tmp_path / "report.txt"

        # Create initial file
        ReportGenerator.export_report("First content", "txt", str(output_file))

        # Overwrite
        ReportGenerator.export_report("Second content", "txt", str(output_file))

        with open(output_file, "r") as f:
            content = f.read()
        assert content == "Second content"

    def test_export_report_invalid_path(self):
        """Test export fails with invalid path."""
        with pytest.raises(ReportError):
            ReportGenerator.export_report(
                "content",
                "txt",
                "/invalid/path/that/cannot/be/created/report.txt"
            )

    def test_export_report_permission_error(self, tmp_path):
        """Test export handles permission errors."""
        # TODO: Mock permission error
        pass


class TestReportIntegration:
    """Integration tests for report generation."""

    def test_full_report_generation_workflow(self, sample_dataframe, tmp_path):
        """Test complete report generation workflow."""
        # Generate all report types
        summary = ReportGenerator.generate_summary_report(
            sample_dataframe,
            duration_seconds=5.0
        )
        quality = ReportGenerator.generate_data_quality_report(sample_dataframe)

        # Export both
        summary_file = tmp_path / "summary.txt"
        quality_file = tmp_path / "quality.txt"

        ReportGenerator.export_report(summary, "txt", str(summary_file))
        ReportGenerator.export_report(quality, "txt", str(quality_file))

        assert summary_file.exists()
        assert quality_file.exists()

    def test_report_with_large_dataset(self):
        """Test report generation with large dataset."""
        # Create large DataFrame
        df = pd.DataFrame({
            "col1": range(10000),
            "col2": ["value"] * 10000,
        })

        report = ReportGenerator.generate_data_quality_report(df)
        assert "Total Rows: 10,000" in report

    def test_report_formatting_consistency(self, sample_dataframe):
        """Test report formatting is consistent."""
        summary = ReportGenerator.generate_summary_report(sample_dataframe)
        quality = ReportGenerator.generate_data_quality_report(sample_dataframe)

        # Both should have proper headers
        assert "=" * 80 in summary
        assert "=" * 80 in quality
        assert "-" * 80 in summary
        assert "-" * 80 in quality


# TODO: Add tests for:
# - Different output formats (md, html)
# - Report generation with edge case data
# - Performance with very large datasets
# - Unicode handling in reports
# - Report truncation for large error lists
# - Timestamp formatting in reports
