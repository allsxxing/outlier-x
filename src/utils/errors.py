"""Custom exception classes for outlier-x."""


class OutlierException(Exception):
    """Base exception class for all outlier-x errors."""

    pass


class ConfigurationError(OutlierException):
    """Raised when configuration is invalid or missing."""

    pass


class IngestionError(OutlierException):
    """Raised when data ingestion fails."""

    pass


class NormalizationError(OutlierException):
    """Raised when data normalization fails."""

    pass


class ValidationError(OutlierException):
    """Raised when data validation fails."""

    pass


class ReportError(OutlierException):
    """Raised when report generation fails."""

    pass


class CLIError(OutlierException):
    """Raised when CLI execution fails."""

    pass
