"""Report generation module for outlier-x."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from src.validate import ValidationReport
from src.utils.errors import ReportError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ReportGenerator:
    """Generator for various report types."""

    @staticmethod
    def generate_summary_report(
        data: pd.DataFrame,
        stats: Optional[Dict[str, Any]] = None,
        duration_seconds: float = 0.0,
    ) -> str:
        """
        Generate a summary report.

        Args:
            data: Processed DataFrame
            stats: Optional dictionary of additional statistics
            duration_seconds: Processing duration

        Returns:
            Formatted summary report as string
        """
        try:
            stats = stats or {}

            report_lines = [
                "=" * 80,
                "OUTLIER.BET DATA PROCESSING SUMMARY REPORT",
                "=" * 80,
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "RECORD STATISTICS",
                "-" * 80,
                f"Total Records Processed: {len(data):,}",
                f"Columns: {', '.join(data.columns.tolist())}",
                f"Memory Usage: {data.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
                "",
                "PROCESSING STATISTICS",
                "-" * 80,
                f"Processing Duration: {duration_seconds:.2f} seconds",
                f"Records Per Second: {len(data) / duration_seconds:.0f}" if duration_seconds > 0 else "N/A",
                "",
            ]

            if stats:
                report_lines.extend(["ADDITIONAL STATISTICS", "-" * 80])
                for key, value in stats.items():
                    report_lines.append(f"{key}: {value}")
                report_lines.append("")

            report_lines.extend(["=" * 80])

            return "\n".join(report_lines)
        except Exception as e:
            raise ReportError(f"Failed to generate summary report: {e}")

    @staticmethod
    def generate_validation_report(result: ValidationReport) -> str:
        """
        Generate a validation report.

        Args:
            result: ValidationReport instance

        Returns:
            Formatted validation report as string
        """
        try:
            data_dict = result.to_dict()

            report_lines = [
                "=" * 80,
                "DATA VALIDATION REPORT",
                "=" * 80,
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "VALIDATION SUMMARY",
                "-" * 80,
                f"Total Records: {data_dict['total_records']:,}",
                f"Valid Records: {data_dict['valid_records']:,}",
                f"Invalid Records: {data_dict['invalid_records']:,}",
                f"Validity Rate: {data_dict['validity_percentage']:.2f}%",
                "",
                "ERRORS BY FIELD",
                "-" * 80,
            ]

            if data_dict["errors_by_field"]:
                for field, count in sorted(
                    data_dict["errors_by_field"].items(), key=lambda x: x[1], reverse=True
                ):
                    report_lines.append(f"  {field}: {count} errors")
            else:
                report_lines.append("  No errors found")

            report_lines.append("")

            if data_dict["error_samples"]:
                report_lines.extend(["ERROR SAMPLES (First 10)", "-" * 80])
                for i, sample in enumerate(data_dict["error_samples"], 1):
                    report_lines.append(
                        f"{i}. Field: {sample['field']}, Value: {sample['value']}, Error: {sample['error']}"
                    )
                report_lines.append("")

            if data_dict["warnings"]:
                report_lines.extend(["WARNINGS", "-" * 80])
                for warning in data_dict["warnings"]:
                    report_lines.append(f"  - {warning}")
                report_lines.append("")

            report_lines.extend(["=" * 80])

            return "\n".join(report_lines)
        except Exception as e:
            raise ReportError(f"Failed to generate validation report: {e}")

    @staticmethod
    def generate_data_quality_report(df: pd.DataFrame) -> str:
        """
        Generate a data quality report.

        Args:
            df: Input DataFrame

        Returns:
            Formatted data quality report as string
        """
        try:
            report_lines = [
                "=" * 80,
                "DATA QUALITY REPORT",
                "=" * 80,
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "DATASET OVERVIEW",
                "-" * 80,
                f"Total Rows: {len(df):,}",
                f"Total Columns: {len(df.columns)}",
                "",
                "FIELD QUALITY METRICS",
                "-" * 80,
            ]

            for column in df.columns:
                total = len(df)
                non_null = df[column].notna().sum()
                null_count = df[column].isna().sum()
                completeness = (non_null / total * 100) if total > 0 else 0

                report_lines.append(f"{column}:")
                report_lines.append(f"  Completeness: {completeness:.2f}%")
                report_lines.append(f"  Non-Null Values: {non_null:,}")
                report_lines.append(f"  Null Values: {null_count:,}")

                if df[column].dtype in ["int64", "float64"]:
                    report_lines.append(f"  Min: {df[column].min()}")
                    report_lines.append(f"  Max: {df[column].max()}")
                    report_lines.append(f"  Mean: {df[column].mean():.2f}")

                # Uniqueness
                unique_count = df[column].nunique()
                uniqueness = (unique_count / total * 100) if total > 0 else 0
                report_lines.append(f"  Uniqueness: {uniqueness:.2f}% ({unique_count:,} unique)")
                report_lines.append("")

            report_lines.extend(["=" * 80])

            return "\n".join(report_lines)
        except Exception as e:
            raise ReportError(f"Failed to generate data quality report: {e}")

    @staticmethod
    def export_report(report: str, format: str, path: str) -> None:
        """
        Export report to file.

        Args:
            report: Report content as string
            format: Output format ('txt', 'md', 'html')
            path: Output file path

        Raises:
            ReportError: If export fails
        """
        try:
            output_path = Path(path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w") as f:
                f.write(report)

            logger.info(f"Report exported to {output_path}")
        except Exception as e:
            raise ReportError(f"Failed to export report: {e}")
