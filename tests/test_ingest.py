"""Tests for the ingest module."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import pandas as pd

from src.ingest import JSONSource, CSVSource, APISource, IngestionManager
from src.utils.errors import IngestionError


@pytest.fixture
def sample_json_file(tmp_path):
    """Create a sample JSON file for testing."""
    data = [
        {"event_id": "evt_001", "sport": "football", "volume": 1000},
        {"event_id": "evt_002", "sport": "basketball", "volume": 2000},
    ]
    json_file = tmp_path / "sample.json"
    with open(json_file, "w") as f:
        json.dump(data, f)
    return json_file


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file for testing."""
    csv_file = tmp_path / "sample.csv"
    df = pd.DataFrame({
        "event_id": ["evt_001", "evt_002"],
        "sport": ["football", "basketball"],
        "volume": [1000, 2000]
    })
    df.to_csv(csv_file, index=False)
    return csv_file


class TestJSONSource:
    """Test JSONSource class."""

    def test_json_source_fetch_array(self, sample_json_file):
        """Test fetching from JSON array."""
        source = JSONSource(str(sample_json_file))
        data = source.fetch()
        assert len(data) == 2
        assert data[0]["event_id"] == "evt_001"

    def test_json_source_fetch_object(self, tmp_path):
        """Test fetching from JSON object."""
        json_file = tmp_path / "single.json"
        with open(json_file, "w") as f:
            json.dump({"event_id": "evt_001", "sport": "football"}, f)

        source = JSONSource(str(json_file))
        data = source.fetch()
        assert len(data) == 1
        assert data[0]["event_id"] == "evt_001"

    def test_json_source_file_not_found(self):
        """Test error when JSON file not found."""
        source = JSONSource("nonexistent.json")
        assert not source.validate_connection()

    def test_json_source_invalid_json(self, tmp_path):
        """Test error with invalid JSON."""
        json_file = tmp_path / "invalid.json"
        with open(json_file, "w") as f:
            f.write("invalid json content {")

        source = JSONSource(str(json_file))
        with pytest.raises(IngestionError):
            source.fetch()


class TestCSVSource:
    """Test CSVSource class."""

    def test_csv_source_fetch(self, sample_csv_file):
        """Test fetching from CSV file."""
        source = CSVSource(str(sample_csv_file))
        data = source.fetch()
        assert len(data) == 2
        assert data[0]["event_id"] == "evt_001"

    def test_csv_source_file_not_found(self):
        """Test error when CSV file not found."""
        source = CSVSource("nonexistent.csv")
        assert not source.validate_connection()


class TestAPISource:
    """Test APISource class."""

    @patch("requests.head")
    def test_api_source_validate_connection(self, mock_head):
        """Test API connection validation."""
        mock_head.return_value.status_code = 200
        source = APISource("https://api.example.com/data")
        assert source.validate_connection()

    @patch("requests.get")
    def test_api_source_fetch(self, mock_get):
        """Test fetching from API."""
        mock_response = MagicMock()
        mock_response.json.return_value = [{"event_id": "evt_001"}]
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        source = APISource("https://api.example.com/data")
        data = source.fetch()
        assert len(data) == 1
        assert data[0]["event_id"] == "evt_001"

    @patch("requests.get")
    def test_api_source_fetch_error(self, mock_get):
        """Test API fetch error handling."""
        mock_get.side_effect = Exception("Connection error")

        source = APISource("https://api.example.com/data")
        with pytest.raises(IngestionError):
            source.fetch()


class TestIngestionManager:
    """Test IngestionManager class."""

    def test_load_from_source(self, sample_json_file):
        """Test loading from source."""
        source = JSONSource(str(sample_json_file))
        df = IngestionManager.load_from_source(source)
        assert len(df) == 2
        assert isinstance(df, pd.DataFrame)

    def test_merge_sources(self, sample_json_file, sample_csv_file):
        """Test merging multiple sources."""
        sources = [JSONSource(str(sample_json_file)), CSVSource(str(sample_csv_file))]
        df = IngestionManager.merge_sources(sources)
        assert len(df) == 4

    def test_deduplicate(self, sample_json_file):
        """Test deduplication."""
        source = JSONSource(str(sample_json_file))
        df = IngestionManager.load_from_source(source)

        # Add duplicate
        df_with_dups = pd.concat([df, df.iloc[[0]]], ignore_index=True)
        assert len(df_with_dups) == 3

        df_deduplicated = IngestionManager.deduplicate(df_with_dups, "event_id")
        assert len(df_deduplicated) == 2

    def test_deduplicate_missing_key(self, sample_json_file):
        """Test deduplication with missing key column."""
        source = JSONSource(str(sample_json_file))
        df = IngestionManager.load_from_source(source)

        with pytest.raises(IngestionError):
            IngestionManager.deduplicate(df, "nonexistent_column")
