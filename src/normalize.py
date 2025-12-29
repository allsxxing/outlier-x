"""Data normalization module for outlier-x."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from src.utils.constants import DEFAULT_DECIMAL_PLACES, DEFAULT_ODDS_FORMAT, MIN_ODDS_VALUE
from src.utils.errors import NormalizationError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class NormalizationEngine:
    """Engine for data normalization operations."""

    @staticmethod
    def normalize_timestamp(
        value: Any, format: str = "%Y-%m-%d %H:%M:%S"
    ) -> Optional[datetime]:
        """
        Normalize a timestamp value.

        Args:
            value: Value to normalize
            format: Expected datetime format

        Returns:
            Normalized datetime object or None if value is None

        Raises:
            NormalizationError: If value cannot be parsed as datetime
        """
        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        try:
            if isinstance(value, str):
                return datetime.strptime(value, format)
            elif isinstance(value, (int, float)):
                # Assume Unix timestamp
                return datetime.fromtimestamp(value)
            else:
                raise NormalizationError(
                    f"Cannot normalize timestamp of type {type(value)}: {value}"
                )
        except ValueError as e:
            raise NormalizationError(f"Invalid timestamp format: {value}, error: {e}")

    @staticmethod
    def normalize_numeric(value: Any, decimal_places: int = DEFAULT_DECIMAL_PLACES) -> Optional[float]:
        """
        Normalize a numeric value.

        Args:
            value: Value to normalize
            decimal_places: Number of decimal places to round to

        Returns:
            Rounded float or None if value is None

        Raises:
            NormalizationError: If value cannot be converted to float
        """
        if value is None:
            return None

        try:
            numeric_value = float(value)
            return round(numeric_value, decimal_places)
        except (TypeError, ValueError) as e:
            raise NormalizationError(f"Cannot convert to numeric: {value}, error: {e}")

    @staticmethod
    def normalize_string(value: Any, case: str = "lower") -> Optional[str]:
        """
        Normalize a string value.

        Args:
            value: Value to normalize
            case: Case transformation ('lower', 'upper', 'title', 'original')

        Returns:
            Normalized string or None if value is None

        Raises:
            NormalizationError: If value cannot be converted to string
        """
        if value is None:
            return None

        try:
            string_value = str(value).strip()
            if case == "lower":
                return string_value.lower()
            elif case == "upper":
                return string_value.upper()
            elif case == "title":
                return string_value.title()
            else:
                return string_value
        except Exception as e:
            raise NormalizationError(f"Cannot normalize string: {value}, error: {e}")

    @staticmethod
    def normalize_boolean(value: Any) -> Optional[bool]:
        """
        Normalize a boolean value.

        Args:
            value: Value to normalize

        Returns:
            Boolean value or None if value is None

        Raises:
            NormalizationError: If value cannot be converted to boolean
        """
        if value is None:
            return None

        if isinstance(value, bool):
            return value

        try:
            string_value = str(value).lower().strip()
            if string_value in ("true", "1", "yes", "on"):
                return True
            elif string_value in ("false", "0", "no", "off"):
                return False
            else:
                raise NormalizationError(f"Cannot convert to boolean: {value}")
        except Exception as e:
            raise NormalizationError(f"Cannot normalize boolean: {value}, error: {e}")

    @staticmethod
    def normalize_currency(value: Any, currency: str = "USD") -> Optional[float]:
        """
        Normalize a currency value.

        Args:
            value: Value to normalize
            currency: Currency code (informational)

        Returns:
            Float value or None if value is None

        Raises:
            NormalizationError: If value cannot be normalized
        """
        if value is None:
            return None

        try:
            # Remove common currency symbols
            if isinstance(value, str):
                cleaned = value.replace("$", "").replace("€", "").replace("£", "").strip()
                return NormalizationEngine.normalize_numeric(cleaned, decimal_places=2)
            else:
                return NormalizationEngine.normalize_numeric(value, decimal_places=2)
        except Exception as e:
            raise NormalizationError(f"Cannot normalize currency: {value}, error: {e}")

    @staticmethod
    def normalize_odds(value: Any, format: str = DEFAULT_ODDS_FORMAT) -> Optional[float]:
        """
        Normalize odds value.

        Args:
            value: Value to normalize
            format: Odds format ('decimal', 'fractional', 'moneyline')

        Returns:
            Decimal odds or None if value is None

        Raises:
            NormalizationError: If odds value is invalid
        """
        if value is None:
            return None

        try:
            numeric_value = NormalizationEngine.normalize_numeric(value, decimal_places=4)
            if numeric_value is None:
                return None

            if numeric_value < MIN_ODDS_VALUE:
                raise NormalizationError(f"Odds value below minimum ({MIN_ODDS_VALUE}): {value}")

            return numeric_value
        except Exception as e:
            raise NormalizationError(f"Cannot normalize odds: {value}, error: {e}")

    @staticmethod
    def normalize_field(value: Any, field_name: str, rules: Dict[str, Any]) -> Any:
        """
        Normalize a field value based on rules.

        Args:
            value: Value to normalize
            field_name: Name of field
            rules: Normalization rules dict

        Returns:
            Normalized value

        Raises:
            NormalizationError: If normalization fails
        """
        try:
            field_type = rules.get("type", "string")

            if field_type == "timestamp":
                format_str = rules.get("format", "%Y-%m-%d %H:%M:%S")
                return NormalizationEngine.normalize_timestamp(value, format_str)
            elif field_type == "numeric":
                decimal_places = rules.get("decimal_places", DEFAULT_DECIMAL_PLACES)
                return NormalizationEngine.normalize_numeric(value, decimal_places)
            elif field_type == "boolean":
                return NormalizationEngine.normalize_boolean(value)
            elif field_type == "currency":
                currency = rules.get("currency", "USD")
                return NormalizationEngine.normalize_currency(value, currency)
            elif field_type == "odds":
                odds_format = rules.get("format", DEFAULT_ODDS_FORMAT)
                return NormalizationEngine.normalize_odds(value, odds_format)
            else:  # string or default
                case = rules.get("case", "original")
                return NormalizationEngine.normalize_string(value, case)
        except Exception as e:
            raise NormalizationError(f"Failed to normalize field '{field_name}': {e}")

    @staticmethod
    def normalize_row(row: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a single row based on schema.

        Args:
            row: Row data as dictionary
            schema: Schema defining field types and rules

        Returns:
            Normalized row

        Raises:
            NormalizationError: If normalization fails
        """
        try:
            normalized_row = {}
            for field_name, field_schema in schema.items():
                value = row.get(field_name)
                normalized_row[field_name] = NormalizationEngine.normalize_field(
                    value, field_name, field_schema
                )
            return normalized_row
        except Exception as e:
            raise NormalizationError(f"Failed to normalize row: {e}")

    @staticmethod
    def normalize_dataframe(df: pd.DataFrame, schema: Dict[str, Any]) -> pd.DataFrame:
        """
        Normalize all rows in a DataFrame.

        Args:
            df: Input DataFrame
            schema: Schema defining field types and rules

        Returns:
            Normalized DataFrame

        Raises:
            NormalizationError: If normalization fails
        """
        try:
            records = df.to_dict("records")
            normalized_records = [
                NormalizationEngine.normalize_row(record, schema) for record in records
            ]
            normalized_df = pd.DataFrame(normalized_records)
            logger.info(f"Normalized {len(normalized_df)} records")
            return normalized_df
        except Exception as e:
            raise NormalizationError(f"Failed to normalize DataFrame: {e}")
