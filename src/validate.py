"""Data validation module for outlier-x."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

from src.utils.errors import ValidationError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ValidationResult:
    """Result of validating a single field."""

    field_name: str
    value: Any
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    """Report from validating a full dataset."""

    total_records: int
    valid_records: int
    invalid_records: int
    warnings: List[str] = field(default_factory=list)
    errors_by_field: Dict[str, int] = field(default_factory=dict)
    error_samples: List[Dict[str, Any]] = field(default_factory=list)
    max_error_samples: int = 10

    def add_error_sample(self, field_name: str, value: Any, error: str) -> None:
        """Add an error sample to the report."""
        if len(self.error_samples) < self.max_error_samples:
            self.error_samples.append(
                {"field": field_name, "value": value, "error": error}
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "total_records": self.total_records,
            "valid_records": self.valid_records,
            "invalid_records": self.invalid_records,
            "validity_percentage": (
                100 * self.valid_records / self.total_records
                if self.total_records > 0
                else 0
            ),
            "warnings": self.warnings,
            "errors_by_field": self.errors_by_field,
            "error_samples": self.error_samples,
        }


class ValidationEngine:
    """Engine for data validation operations."""

    @staticmethod
    def validate_required(value: Any, field_name: str) -> ValidationResult:
        """Validate that a required field is not null."""
        result = ValidationResult(field_name, value, is_valid=True)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            result.is_valid = False
            result.errors.append(f"Required field '{field_name}' is null or empty")
        return result

    @staticmethod
    def validate_type(
        value: Any, field_name: str, expected_type: type
    ) -> ValidationResult:
        """Validate that a field matches expected type."""
        result = ValidationResult(field_name, value, is_valid=True)
        if value is not None and not isinstance(value, expected_type):
            result.is_valid = False
            result.errors.append(
                f"Field '{field_name}' has type {type(value).__name__}, expected {expected_type.__name__}"
            )
        return result

    @staticmethod
    def validate_range(
        value: Any, field_name: str, min_value: Optional[float] = None, max_value: Optional[float] = None
    ) -> ValidationResult:
        """Validate that a numeric field is within range."""
        result = ValidationResult(field_name, value, is_valid=True)
        if value is None:
            return result

        try:
            numeric_value = float(value)
            if min_value is not None and numeric_value < min_value:
                result.is_valid = False
                result.errors.append(
                    f"Field '{field_name}' value {numeric_value} below minimum {min_value}"
                )
            if max_value is not None and numeric_value > max_value:
                result.is_valid = False
                result.errors.append(
                    f"Field '{field_name}' value {numeric_value} above maximum {max_value}"
                )
        except (TypeError, ValueError) as e:
            result.is_valid = False
            result.errors.append(f"Cannot compare {field_name} as numeric: {e}")

        return result

    @staticmethod
    def validate_length(
        value: Any,
        field_name: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ) -> ValidationResult:
        """Validate string length."""
        result = ValidationResult(field_name, value, is_valid=True)
        if value is None:
            return result

        try:
            str_value = str(value)
            length = len(str_value)
            if min_length is not None and length < min_length:
                result.is_valid = False
                result.errors.append(
                    f"Field '{field_name}' length {length} below minimum {min_length}"
                )
            if max_length is not None and length > max_length:
                result.is_valid = False
                result.errors.append(
                    f"Field '{field_name}' length {length} above maximum {max_length}"
                )
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Cannot validate length of {field_name}: {e}")

        return result

    @staticmethod
    def validate_pattern(value: Any, field_name: str, pattern: str) -> ValidationResult:
        """Validate that a field matches a regex pattern."""
        import re

        result = ValidationResult(field_name, value, is_valid=True)
        if value is None:
            return result

        try:
            if not re.match(pattern, str(value)):
                result.is_valid = False
                result.errors.append(
                    f"Field '{field_name}' value '{value}' does not match pattern '{pattern}'"
                )
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Error validating pattern for {field_name}: {e}")

        return result

    @staticmethod
    def validate_enum(value: Any, field_name: str, allowed_values: List[Any]) -> ValidationResult:
        """Validate that a field is in allowed values."""
        result = ValidationResult(field_name, value, is_valid=True)
        if value is None:
            return result

        if value not in allowed_values:
            result.is_valid = False
            result.errors.append(
                f"Field '{field_name}' value '{value}' not in allowed values: {allowed_values}"
            )

        return result

    @staticmethod
    def validate_custom(
        value: Any, field_name: str, validator_func: Callable[[Any], bool]
    ) -> ValidationResult:
        """Validate using a custom validation function."""
        result = ValidationResult(field_name, value, is_valid=True)
        try:
            if not validator_func(value):
                result.is_valid = False
                result.errors.append(f"Custom validation failed for field '{field_name}'")
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Error in custom validation for {field_name}: {e}")

        return result

    @staticmethod
    def validate_field(value: Any, field_name: str, rules: Dict[str, Any]) -> ValidationResult:
        """
        Validate a field against a set of rules.

        Args:
            value: Value to validate
            field_name: Name of the field
            rules: Validation rules dictionary

        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult(field_name, value, is_valid=True)

        try:
            # Check required
            if rules.get("required", False):
                required_result = ValidationEngine.validate_required(value, field_name)
                if not required_result.is_valid:
                    result.is_valid = False
                    result.errors.extend(required_result.errors)
                    return result

            # Skip remaining validations if value is null and field is nullable
            if value is None and rules.get("nullable", True):
                return result

            # Check type
            if "type" in rules and value is not None:
                type_result = ValidationEngine.validate_type(value, field_name, rules["type"])
                if not type_result.is_valid:
                    result.is_valid = False
                    result.errors.extend(type_result.errors)

            # Check range
            if rules.get("min_value") is not None or rules.get("max_value") is not None:
                range_result = ValidationEngine.validate_range(
                    value, field_name, rules.get("min_value"), rules.get("max_value")
                )
                if not range_result.is_valid:
                    result.is_valid = False
                    result.errors.extend(range_result.errors)

            # Check length
            if rules.get("min_length") is not None or rules.get("max_length") is not None:
                length_result = ValidationEngine.validate_length(
                    value,
                    field_name,
                    rules.get("min_length"),
                    rules.get("max_length"),
                )
                if not length_result.is_valid:
                    result.is_valid = False
                    result.errors.extend(length_result.errors)

            # Check pattern
            if "pattern" in rules and value is not None:
                pattern_result = ValidationEngine.validate_pattern(
                    value, field_name, rules["pattern"]
                )
                if not pattern_result.is_valid:
                    result.is_valid = False
                    result.errors.extend(pattern_result.errors)

            # Check enum
            if "enum" in rules and value is not None:
                enum_result = ValidationEngine.validate_enum(value, field_name, rules["enum"])
                if not enum_result.is_valid:
                    result.is_valid = False
                    result.errors.extend(enum_result.errors)

            # Custom validation
            if "custom" in rules and callable(rules["custom"]):
                custom_result = ValidationEngine.validate_custom(
                    value, field_name, rules["custom"]
                )
                if not custom_result.is_valid:
                    result.is_valid = False
                    result.errors.extend(custom_result.errors)

        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Unexpected error validating {field_name}: {e}")

        return result

    @staticmethod
    def validate_row(row: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
        """
        Validate a single row against schema.

        Args:
            row: Row data as dictionary
            schema: Schema with validation rules

        Returns:
            ValidationResult combining all field validations
        """
        row_result = ValidationResult("row", row, is_valid=True)

        for field_name, field_rules in schema.items():
            value = row.get(field_name)
            field_result = ValidationEngine.validate_field(value, field_name, field_rules)

            if not field_result.is_valid:
                row_result.is_valid = False
                row_result.errors.extend(field_result.errors)
            row_result.warnings.extend(field_result.warnings)

        return row_result

    @staticmethod
    def validate_dataframe(df: pd.DataFrame, schema: Dict[str, Any]) -> ValidationReport:
        """
        Validate all rows in a DataFrame.

        Args:
            df: Input DataFrame
            schema: Schema with validation rules

        Returns:
            ValidationReport with detailed validation results

        Raises:
            ValidationError: If validation process fails
        """
        try:
            report = ValidationReport(
                total_records=len(df),
                valid_records=0,
                invalid_records=0,
            )

            records = df.to_dict("records")

            for record in records:
                result = ValidationEngine.validate_row(record, schema)

                if result.is_valid:
                    report.valid_records += 1
                else:
                    report.invalid_records += 1
                    for error in result.errors:
                        # Extract field name from error message
                        field_name = "unknown"
                        if "'" in error:
                            parts = error.split("'")
                            if len(parts) >= 2:
                                field_name = parts[1]
                        report.errors_by_field[field_name] = (
                            report.errors_by_field.get(field_name, 0) + 1
                        )
                        report.add_error_sample(field_name, record.get(field_name), error)

                report.warnings.extend(result.warnings)

            logger.info(
                f"Validation complete: {report.valid_records}/{report.total_records} valid"
            )
            return report
        except Exception as e:
            raise ValidationError(f"Failed to validate DataFrame: {e}")
