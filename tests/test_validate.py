"""Tests for the validate module."""

import pytest
import pandas as pd

from src.validate import ValidationEngine, ValidationResult, ValidationReport
from src.utils.errors import ValidationError


class TestValidationResult:
    """Test ValidationResult class."""

    def test_validation_result_valid(self):
        """Test creating a valid result."""
        result = ValidationResult("field1", "value1", is_valid=True)
        assert result.is_valid
        assert result.errors == []

    def test_validation_result_invalid(self):
        """Test creating an invalid result."""
        result = ValidationResult("field1", "value1", is_valid=False)
        result.errors.append("Test error")
        assert not result.is_valid
        assert len(result.errors) == 1


class TestValidateRequired:
    """Test required field validation."""

    def test_required_valid(self):
        """Test valid required field."""
        result = ValidationEngine.validate_required("value", "field1")
        assert result.is_valid

    def test_required_null(self):
        """Test null required field."""
        result = ValidationEngine.validate_required(None, "field1")
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_required_empty_string(self):
        """Test empty string required field."""
        result = ValidationEngine.validate_required("", "field1")
        assert not result.is_valid


class TestValidateType:
    """Test type validation."""

    def test_type_valid(self):
        """Test valid type."""
        result = ValidationEngine.validate_type("hello", "field1", str)
        assert result.is_valid

    def test_type_invalid(self):
        """Test invalid type."""
        result = ValidationEngine.validate_type(123, "field1", str)
        assert not result.is_valid

    def test_type_null_allowed(self):
        """Test null value skips type check."""
        result = ValidationEngine.validate_type(None, "field1", str)
        assert result.is_valid


class TestValidateRange:
    """Test numeric range validation."""

    def test_range_valid(self):
        """Test value in valid range."""
        result = ValidationEngine.validate_range(50, "field1", min_value=0, max_value=100)
        assert result.is_valid

    def test_range_below_minimum(self):
        """Test value below minimum."""
        result = ValidationEngine.validate_range(-10, "field1", min_value=0, max_value=100)
        assert not result.is_valid

    def test_range_above_maximum(self):
        """Test value above maximum."""
        result = ValidationEngine.validate_range(150, "field1", min_value=0, max_value=100)
        assert not result.is_valid


class TestValidateLength:
    """Test string length validation."""

    def test_length_valid(self):
        """Test valid string length."""
        result = ValidationEngine.validate_length("hello", "field1", min_length=2, max_length=10)
        assert result.is_valid

    def test_length_too_short(self):
        """Test string too short."""
        result = ValidationEngine.validate_length("hi", "field1", min_length=5, max_length=10)
        assert not result.is_valid

    def test_length_too_long(self):
        """Test string too long."""
        result = ValidationEngine.validate_length("hello world", "field1", min_length=2, max_length=10)
        assert not result.is_valid


class TestValidateEnum:
    """Test enum validation."""

    def test_enum_valid(self):
        """Test valid enum value."""
        result = ValidationEngine.validate_enum("football", "sport", ["football", "basketball"])
        assert result.is_valid

    def test_enum_invalid(self):
        """Test invalid enum value."""
        result = ValidationEngine.validate_enum("tennis", "sport", ["football", "basketball"])
        assert not result.is_valid


class TestValidateField:
    """Test complete field validation."""

    def test_validate_field_required(self):
        """Test field validation with required rule."""
        rules = {"required": True}
        result = ValidationEngine.validate_field(None, "field1", rules)
        assert not result.is_valid

    def test_validate_field_type_and_range(self):
        """Test field validation with multiple rules."""
        rules = {"type": int, "min_value": 0, "max_value": 100}
        result = ValidationEngine.validate_field(50, "field1", rules)
        assert result.is_valid

        result = ValidationEngine.validate_field(150, "field1", rules)
        assert not result.is_valid


class TestValidateRow:
    """Test row validation."""

    def test_validate_row_valid(self):
        """Test validating a valid row."""
        row = {
            "event_id": "evt_001",
            "sport": "football",
            "volume": 1000
        }
        schema = {
            "event_id": {"required": True, "type": str},
            "sport": {"required": True, "type": str, "enum": ["football", "basketball"]},
            "volume": {"required": True, "type": int, "min_value": 0}
        }
        result = ValidationEngine.validate_row(row, schema)
        assert result.is_valid

    def test_validate_row_invalid(self):
        """Test validating an invalid row."""
        row = {
            "event_id": None,
            "sport": "tennis",
            "volume": -100
        }
        schema = {
            "event_id": {"required": True, "type": str},
            "sport": {"required": True, "type": str, "enum": ["football", "basketball"]},
            "volume": {"required": True, "type": int, "min_value": 0}
        }
        result = ValidationEngine.validate_row(row, schema)
        assert not result.is_valid
        assert len(result.errors) > 0


class TestValidateDataFrame:
    """Test DataFrame validation."""

    def test_validate_dataframe(self):
        """Test validating a DataFrame."""
        df = pd.DataFrame({
            "event_id": ["evt_001", "evt_002"],
            "sport": ["football", "basketball"],
            "volume": [1000, 2000]
        })
        schema = {
            "event_id": {"required": True, "type": str},
            "sport": {"required": True, "type": str},
            "volume": {"required": True, "type": int, "min_value": 0}
        }
        report = ValidationEngine.validate_dataframe(df, schema)
        assert report.valid_records == 2
        assert report.invalid_records == 0

    def test_validate_dataframe_with_errors(self):
        """Test validating DataFrame with invalid records."""
        df = pd.DataFrame({
            "event_id": ["evt_001", None],
            "sport": ["football", "tennis"],
            "volume": [1000, -100]
        })
        schema = {
            "event_id": {"required": True, "type": str},
            "sport": {"required": True, "type": str, "enum": ["football", "basketball"]},
            "volume": {"required": True, "type": int, "min_value": 0}
        }
        report = ValidationEngine.validate_dataframe(df, schema)
        assert report.valid_records == 0
        assert report.invalid_records == 2
