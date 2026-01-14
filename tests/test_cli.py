"""Tests for the CLI entry point."""

import subprocess
import sys


class TestCLIEntryPoint:
    """Test the cli.py entry point."""

    def test_cli_help(self):
        """Test that 'python cli.py --help' works."""
        result = subprocess.run(
            [sys.executable, "cli.py", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Outlier.bet Ingest Protocol" in result.stdout
        assert "Commands:" in result.stdout
        assert "ingest" in result.stdout
        assert "normalize" in result.stdout
        assert "validate" in result.stdout
        assert "process" in result.stdout
        assert "report" in result.stdout

    def test_cli_ingest_help(self):
        """Test that 'python cli.py ingest --help' works."""
        result = subprocess.run(
            [sys.executable, "cli.py", "ingest", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Ingest data from specified source" in result.stdout
        assert "--source" in result.stdout
        assert "--path" in result.stdout

    def test_cli_normalize_help(self):
        """Test that 'python cli.py normalize --help' works."""
        result = subprocess.run(
            [sys.executable, "cli.py", "normalize", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Normalize data" in result.stdout
        assert "--input" in result.stdout

    def test_cli_validate_help(self):
        """Test that 'python cli.py validate --help' works."""
        result = subprocess.run(
            [sys.executable, "cli.py", "validate", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Validate data" in result.stdout
        assert "--input" in result.stdout
        assert "--strict" in result.stdout

    def test_cli_process_help(self):
        """Test that 'python cli.py process --help' works."""
        result = subprocess.run(
            [sys.executable, "cli.py", "process", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Full pipeline" in result.stdout
        assert "--source" in result.stdout

    def test_cli_report_help(self):
        """Test that 'python cli.py report --help' works."""
        result = subprocess.run(
            [sys.executable, "cli.py", "report", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Generate data quality report" in result.stdout
        assert "--input" in result.stdout
