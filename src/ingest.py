"""Data ingestion module for outlier-x."""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from src.utils.errors import IngestionError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DataSource(ABC):
    """Abstract base class for data sources."""

    @abstractmethod
    def fetch(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Fetch data from source.

        Args:
            **kwargs: Source-specific parameters

        Returns:
            List of dictionaries containing raw data

        Raises:
            IngestionError: If fetch operation fails
        """
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate connection to data source.

        Returns:
            True if connection successful, False otherwise
        """
        pass


class JSONSource(DataSource):
    """Data source for JSON files."""

    def __init__(self, file_path: str):
        """
        Initialize JSON source.

        Args:
            file_path: Path to JSON file
        """
        self.file_path = Path(file_path)

    def validate_connection(self) -> bool:
        """Validate JSON file exists and is readable."""
        if not self.file_path.exists():
            logger.warning(f"JSON file not found: {self.file_path}")
            return False
        return True

    def fetch(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Fetch data from JSON file.

        Args:
            **kwargs: Unused

        Returns:
            List of dictionaries from JSON file

        Raises:
            IngestionError: If file cannot be read or parsed
        """
        try:
            if not self.validate_connection():
                raise IngestionError(f"JSON file not found: {self.file_path}")

            with open(self.file_path, "r") as f:
                data = json.load(f)

            # Handle both single object and array of objects
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                raise IngestionError("JSON file must contain object or array of objects")

            logger.info(f"Fetched {len(data)} records from {self.file_path}")
            return data
        except json.JSONDecodeError as e:
            raise IngestionError(f"Invalid JSON in {self.file_path}: {e}")
        except Exception as e:
            raise IngestionError(f"Error reading JSON file: {e}")


class CSVSource(DataSource):
    """Data source for CSV files."""

    def __init__(self, file_path: str):
        """
        Initialize CSV source.

        Args:
            file_path: Path to CSV file
        """
        self.file_path = Path(file_path)

    def validate_connection(self) -> bool:
        """Validate CSV file exists and is readable."""
        if not self.file_path.exists():
            logger.warning(f"CSV file not found: {self.file_path}")
            return False
        return True

    def fetch(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Fetch data from CSV file.

        Args:
            **kwargs: Optional 'encoding' parameter for CSV

        Returns:
            List of dictionaries from CSV file

        Raises:
            IngestionError: If file cannot be read or parsed
        """
        try:
            if not self.validate_connection():
                raise IngestionError(f"CSV file not found: {self.file_path}")

            encoding = kwargs.get("encoding", "utf-8")
            df = pd.read_csv(self.file_path, encoding=encoding)
            data = df.to_dict("records")

            logger.info(f"Fetched {len(data)} records from {self.file_path}")
            return data
        except Exception as e:
            raise IngestionError(f"Error reading CSV file: {e}")


class APISource(DataSource):
    """Data source for HTTP API endpoints."""

    def __init__(self, url: str):
        """
        Initialize API source.

        Args:
            url: API endpoint URL
        """
        self.url = url

    def validate_connection(self) -> bool:
        """Validate API endpoint is reachable."""
        try:
            response = requests.head(self.url, timeout=5)
            return response.status_code < 500
        except Exception as e:
            logger.warning(f"Cannot reach API: {e}")
            return False

    def fetch(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Fetch data from API endpoint.

        Args:
            **kwargs: Optional 'params' dict for query parameters

        Returns:
            List of dictionaries from API response

        Raises:
            IngestionError: If API request fails
        """
        try:
            if not self.validate_connection():
                raise IngestionError(f"Cannot reach API: {self.url}")

            params = kwargs.get("params", {})
            response = requests.get(self.url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                raise IngestionError("API response must contain object or array of objects")

            logger.info(f"Fetched {len(data)} records from API: {self.url}")
            return data
        except requests.exceptions.RequestException as e:
            raise IngestionError(f"API request failed: {e}")
        except Exception as e:
            raise IngestionError(f"Error parsing API response: {e}")


class IngestionManager:
    """Manager for data ingestion operations."""

    @staticmethod
    def load_from_source(source: DataSource, **kwargs: Any) -> pd.DataFrame:
        """
        Load data from a data source.

        Args:
            source: DataSource instance
            **kwargs: Additional parameters for source.fetch()

        Returns:
            DataFrame with raw data

        Raises:
            IngestionError: If ingestion fails
        """
        try:
            data = source.fetch(**kwargs)
            df = pd.DataFrame(data)
            logger.info(f"Loaded DataFrame with shape {df.shape}")
            return df
        except Exception as e:
            raise IngestionError(f"Failed to load from source: {e}")

    @staticmethod
    def merge_sources(sources: List[DataSource], **kwargs: Any) -> pd.DataFrame:
        """
        Merge data from multiple sources.

        Args:
            sources: List of DataSource instances
            **kwargs: Additional parameters for source.fetch()

        Returns:
            Merged DataFrame

        Raises:
            IngestionError: If merge fails
        """
        try:
            dfs = [
                IngestionManager.load_from_source(source, **kwargs) for source in sources
            ]
            merged_df = pd.concat(dfs, ignore_index=True)
            logger.info(f"Merged {len(sources)} sources into shape {merged_df.shape}")
            return merged_df
        except Exception as e:
            raise IngestionError(f"Failed to merge sources: {e}")

    @staticmethod
    def deduplicate(df: pd.DataFrame, key: str) -> pd.DataFrame:
        """
        Remove duplicate records based on key column.

        Args:
            df: Input DataFrame
            key: Column name to use for deduplication

        Returns:
            DataFrame with duplicates removed

        Raises:
            IngestionError: If key column missing
        """
        try:
            if key not in df.columns:
                raise IngestionError(f"Key column '{key}' not found in DataFrame")

            original_count = len(df)
            df_deduplicated = df.drop_duplicates(subset=[key], keep="first")
            duplicates_removed = original_count - len(df_deduplicated)

            logger.info(f"Removed {duplicates_removed} duplicate records")
            return df_deduplicated
        except Exception as e:
            raise IngestionError(f"Failed to deduplicate data: {e}")
