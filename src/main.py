"""CLI entry point for outlier-x."""

import sys
import time
from pathlib import Path
from typing import Optional

import click
import pandas as pd

from src.config import Config
from src.ingest import CSVSource, JSONSource, APISource, IngestionManager
from src.normalize import NormalizationEngine
from src.report import ReportGenerator
from src.validate import ValidationEngine, ValidationReport
from src.utils.errors import OutlierException
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


# Default schema for validation
DEFAULT_VALIDATION_SCHEMA = {
    "event_id": {"required": True, "type": str, "min_length": 1},
    "sport": {"required": True, "type": str, "enum": ["football", "basketball", "baseball", "hockey"]},
    "event_date": {"required": True, "type": str},
    "teams": {"required": True},
    "odds_provider": {"required": True, "type": str},
    "odds": {"required": True, "type": dict},
    "line": {"required": False, "nullable": True, "type": float},
    "volume": {"required": True, "type": int, "min_value": 0},
    "timestamp": {"required": True, "type": str},
    "data_source": {"required": True, "type": str},
}

# Default schema for normalization
DEFAULT_NORMALIZATION_SCHEMA = {
    "event_id": {"type": "string"},
    "sport": {"type": "string", "case": "lower"},
    "event_date": {"type": "timestamp"},
    "teams": {"type": "string"},
    "odds_provider": {"type": "string", "case": "lower"},
    "odds": {"type": "string"},
    "line": {"type": "numeric", "decimal_places": 2},
    "volume": {"type": "numeric", "decimal_places": 0},
    "timestamp": {"type": "timestamp"},
    "data_source": {"type": "string", "case": "lower"},
}


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Outlier.bet Ingest Protocol - Sports Betting Data Processing CLI."""
    ctx.ensure_object(dict)
    try:
        ctx.obj["config"] = Config.from_env()
        ctx.obj["logger"] = logger
    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--source", required=True, help="Data source (json, csv, api)")
@click.option("--path", help="File path (for json/csv) or URL (for api)")
@click.option("--output", default="data/processed/raw_data.json", help="Output file path")
@click.option("--dry-run", is_flag=True, help="Preview without saving")
@click.pass_context
def ingest(ctx: click.Context, source: str, path: Optional[str], output: str, dry_run: bool) -> None:
    """Ingest data from specified source."""
    try:
        if not path:
            raise click.ClickException("--path is required for ingest command")

        click.echo(f"Ingesting data from {source}: {path}")

        # Create appropriate data source
        if source == "json":
            data_source = JSONSource(path)
        elif source == "csv":
            data_source = CSVSource(path)
        elif source == "api":
            data_source = APISource(path)
        else:
            raise click.ClickException(f"Unknown source type: {source}")

        # Load data
        df = IngestionManager.load_from_source(data_source)
        click.echo(f"✓ Loaded {len(df)} records")

        # Deduplicate
        if "event_id" in df.columns:
            df = IngestionManager.deduplicate(df, "event_id")
            click.echo(f"✓ After deduplication: {len(df)} records")

        if not dry_run:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if output.endswith(".csv"):
                df.to_csv(output_path, index=False)
            else:
                df.to_json(output_path, orient="records")
            click.echo(f"✓ Data saved to {output}")
        else:
            click.echo("✓ Dry run complete (no data saved)")

    except OutlierException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--input", required=True, help="Input file path")
@click.option("--output", default="data/processed/normalized_data.json", help="Output file path")
@click.option("--dry-run", is_flag=True, help="Preview without saving")
@click.pass_context
def normalize(ctx: click.Context, input: str, output: str, dry_run: bool) -> None:
    """Normalize data."""
    try:
        click.echo(f"Normalizing data from {input}")

        # Load data
        if input.endswith(".csv"):
            df = pd.read_csv(input)
        else:
            df = pd.read_json(input)

        # Normalize
        df = NormalizationEngine.normalize_dataframe(df, DEFAULT_NORMALIZATION_SCHEMA)
        click.echo(f"✓ Normalized {len(df)} records")

        if not dry_run:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if output.endswith(".csv"):
                df.to_csv(output_path, index=False)
            else:
                df.to_json(output_path, orient="records")
            click.echo(f"✓ Data saved to {output}")
        else:
            click.echo("✓ Dry run complete (no data saved)")

    except OutlierException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--input", required=True, help="Input file path")
@click.option("--output", default="data/processed/validation_report.txt", help="Report output path")
@click.option("--strict", is_flag=True, help="Fail on any validation error")
@click.pass_context
def validate(ctx: click.Context, input: str, output: str, strict: bool) -> None:
    """Validate data."""
    try:
        click.echo(f"Validating data from {input}")

        # Load data
        if input.endswith(".csv"):
            df = pd.read_csv(input)
        else:
            df = pd.read_json(input)

        # Validate
        report = ValidationEngine.validate_dataframe(df, DEFAULT_VALIDATION_SCHEMA)

        # Generate report
        report_text = ReportGenerator.generate_validation_report(report)
        click.echo(report_text)

        # Save report
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        ReportGenerator.export_report(report_text, "txt", str(output_path))

        if strict and report.invalid_records > 0:
            click.echo(f"Strict mode: {report.invalid_records} invalid records found", err=True)
            sys.exit(1)

    except OutlierException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--source", required=True, help="Data source (json, csv, api)")
@click.option("--path", help="File path (for json/csv) or URL (for api)")
@click.option("--output-dir", default="data/processed", help="Output directory")
@click.option("--strict", is_flag=True, help="Fail on any validation error")
@click.option("--dry-run", is_flag=True, help="Preview without saving")
@click.pass_context
def process(ctx: click.Context, source: str, path: Optional[str], output_dir: str, strict: bool, dry_run: bool) -> None:
    """Full pipeline: ingest → normalize → validate."""
    try:
        start_time = time.time()

        if not path:
            raise click.ClickException("--path is required for process command")

        click.echo("=" * 80)
        click.echo("STARTING FULL DATA PROCESSING PIPELINE")
        click.echo("=" * 80)

        # Step 1: Ingest
        click.echo("\n[1/3] INGESTION")
        click.echo("-" * 80)
        if source == "json":
            data_source = JSONSource(path)
        elif source == "csv":
            data_source = CSVSource(path)
        elif source == "api":
            data_source = APISource(path)
        else:
            raise click.ClickException(f"Unknown source type: {source}")

        df = IngestionManager.load_from_source(data_source)
        click.echo(f"✓ Loaded {len(df)} records")

        if "event_id" in df.columns:
            df = IngestionManager.deduplicate(df, "event_id")
            click.echo(f"✓ Deduplicated to {len(df)} records")

        # Step 2: Normalize
        click.echo("\n[2/3] NORMALIZATION")
        click.echo("-" * 80)
        df = NormalizationEngine.normalize_dataframe(df, DEFAULT_NORMALIZATION_SCHEMA)
        click.echo(f"✓ Normalized {len(df)} records")

        # Step 3: Validate
        click.echo("\n[3/3] VALIDATION")
        click.echo("-" * 80)
        report = ValidationEngine.validate_dataframe(df, DEFAULT_VALIDATION_SCHEMA)
        click.echo(f"✓ Validation complete: {report.valid_records}/{report.total_records} valid")

        # Save results
        if not dry_run:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Save processed data
            df.to_json(output_path / "final_data.json", orient="records")
            click.echo(f"\n✓ Data saved to {output_path / 'final_data.json'}")

            # Save validation report
            report_text = ReportGenerator.generate_validation_report(report)
            ReportGenerator.export_report(report_text, "txt", str(output_path / "validation_report.txt"))

            # Save summary report
            duration = time.time() - start_time
            summary_text = ReportGenerator.generate_summary_report(df, duration_seconds=duration)
            ReportGenerator.export_report(summary_text, "txt", str(output_path / "summary_report.txt"))

            click.echo(f"✓ Reports saved to {output_path}")
        else:
            click.echo("\n✓ Dry run complete (no data saved)")

        if strict and report.invalid_records > 0:
            click.echo(f"\nStrict mode: {report.invalid_records} invalid records found", err=True)
            sys.exit(1)

        duration = time.time() - start_time
        click.echo(f"\n✓ Pipeline completed in {duration:.2f} seconds")

    except OutlierException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--input", required=True, help="Input file path")
@click.option("--output", default="data/processed/report.txt", help="Report output path")
@click.pass_context
def report(ctx: click.Context, input: str, output: str) -> None:
    """Generate data quality report."""
    try:
        click.echo(f"Generating report from {input}")

        # Load data
        if input.endswith(".csv"):
            df = pd.read_csv(input)
        else:
            df = pd.read_json(input)

        # Generate report
        report_text = ReportGenerator.generate_data_quality_report(df)
        click.echo(report_text)

        # Save report
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        ReportGenerator.export_report(report_text, "txt", str(output_path))
        click.echo(f"\n✓ Report saved to {output_path}")

    except OutlierException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli(obj={})
