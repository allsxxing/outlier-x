"""Constants and enumerations for outlier-x."""

from typing import Set

# Supported sports
SPORTS: Set[str] = {"football", "basketball", "baseball", "hockey"}

# Supported output formats
OUTPUT_FORMATS: Set[str] = {"json", "csv", "parquet"}

# Supported log levels
LOG_LEVELS: Set[str] = {"DEBUG", "INFO", "WARNING", "ERROR"}

# Default configuration values
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_BATCH_SIZE = 1000
DEFAULT_OUTPUT_FORMAT = "json"
DEFAULT_STRICT_MODE = False
DEFAULT_DECIMAL_PLACES = 2

# Validation constants
MIN_ODDS_VALUE = 1.0
MIN_VOLUME = 0
DEFAULT_ODDS_FORMAT = "decimal"
