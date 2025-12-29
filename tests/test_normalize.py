"""Tests for the normalize module."""

from datetime import datetime

import pytest

from src.normalize import NormalizationEngine
from src.utils.errors import NormalizationError


class TestNormalizeTimestamp:
    """Test timestamp normalization."""

    def test_normalize_timestamp_string(self):
        """Test normalizing string timestamp."""
        result = NormalizationEngine.normalize_timestamp(
            "2024-12-29 15:30:00", "%Y-%m-%d %H:%M:%S"
        )
        assert isinstance(result, datetime)
        assert result.year == 2024

    def test_normalize_timestamp_datetime(self):
        """Test normalizing datetime object."""
        dt = datetime(2024, 12, 29, 15, 30, 0)
        result = NormalizationEngine.normalize_timestamp(dt)
        assert result == dt

    def test_normalize_timestamp_none(self):
        """Test normalizing None value."""
        result = NormalizationEngine.normalize_timestamp(None)
        assert result is None

    def test_normalize_timestamp_invalid_format(self):
        """Test error on invalid timestamp format."""
        with pytest.raises(NormalizationError):
            NormalizationEngine.normalize_timestamp("invalid_date", "%Y-%m-%d")


class TestNormalizeNumeric:
    """Test numeric normalization."""

    def test_normalize_numeric_float(self):
        """Test normalizing float value."""
        result = NormalizationEngine.normalize_numeric(3.14159, decimal_places=2)
        assert result == 3.14

    def test_normalize_numeric_string(self):
        """Test normalizing numeric string."""
        result = NormalizationEngine.normalize_numeric("42.5", decimal_places=1)
        assert result == 42.5

    def test_normalize_numeric_none(self):
        """Test normalizing None value."""
        result = NormalizationEngine.normalize_numeric(None)
        assert result is None

    def test_normalize_numeric_invalid(self):
        """Test error on invalid numeric value."""
        with pytest.raises(NormalizationError):
            NormalizationEngine.normalize_numeric("not_a_number")


class TestNormalizeString:
    """Test string normalization."""

    def test_normalize_string_lower(self):
        """Test lowercase normalization."""
        result = NormalizationEngine.normalize_string("HELLO", case="lower")
        assert result == "hello"

    def test_normalize_string_upper(self):
        """Test uppercase normalization."""
        result = NormalizationEngine.normalize_string("hello", case="upper")
        assert result == "HELLO"

    def test_normalize_string_title(self):
        """Test title case normalization."""
        result = NormalizationEngine.normalize_string("hello world", case="title")
        assert result == "Hello World"

    def test_normalize_string_trim(self):
        """Test whitespace trimming."""
        result = NormalizationEngine.normalize_string("  hello  ", case="original")
        assert result == "hello"

    def test_normalize_string_none(self):
        """Test normalizing None value."""
        result = NormalizationEngine.normalize_string(None)
        assert result is None


class TestNormalizeBoolean:
    """Test boolean normalization."""

    def test_normalize_boolean_true_values(self):
        """Test normalizing various true values."""
        assert NormalizationEngine.normalize_boolean(True) is True
        assert NormalizationEngine.normalize_boolean("true") is True
        assert NormalizationEngine.normalize_boolean("1") is True
        assert NormalizationEngine.normalize_boolean("yes") is True

    def test_normalize_boolean_false_values(self):
        """Test normalizing various false values."""
        assert NormalizationEngine.normalize_boolean(False) is False
        assert NormalizationEngine.normalize_boolean("false") is False
        assert NormalizationEngine.normalize_boolean("0") is False
        assert NormalizationEngine.normalize_boolean("no") is False

    def test_normalize_boolean_none(self):
        """Test normalizing None value."""
        result = NormalizationEngine.normalize_boolean(None)
        assert result is None

    def test_normalize_boolean_invalid(self):
        """Test error on invalid boolean."""
        with pytest.raises(NormalizationError):
            NormalizationEngine.normalize_boolean("maybe")


class TestNormalizeCurrency:
    """Test currency normalization."""

    def test_normalize_currency_with_symbol(self):
        """Test normalizing currency with symbol."""
        result = NormalizationEngine.normalize_currency("$100.50")
        assert result == 100.50

    def test_normalize_currency_numeric(self):
        """Test normalizing numeric currency."""
        result = NormalizationEngine.normalize_currency(100.50)
        assert result == 100.50

    def test_normalize_currency_none(self):
        """Test normalizing None value."""
        result = NormalizationEngine.normalize_currency(None)
        assert result is None


class TestNormalizeOdds:
    """Test odds normalization."""

    def test_normalize_odds_valid(self):
        """Test normalizing valid odds."""
        result = NormalizationEngine.normalize_odds(1.85)
        assert result == 1.85

    def test_normalize_odds_string(self):
        """Test normalizing odds from string."""
        result = NormalizationEngine.normalize_odds("2.05")
        assert result == 2.05

    def test_normalize_odds_too_low(self):
        """Test error on odds below minimum."""
        with pytest.raises(NormalizationError):
            NormalizationEngine.normalize_odds(0.5)

    def test_normalize_odds_none(self):
        """Test normalizing None value."""
        result = NormalizationEngine.normalize_odds(None)
        assert result is None
