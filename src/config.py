"""Configuration management for outlier-x."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, validator

from src.utils.constants import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_LOG_LEVEL,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_STRICT_MODE,
    LOG_LEVELS,
    OUTPUT_FORMATS,
    SPORTS,
)
from src.utils.errors import ConfigurationError


class Config(BaseModel):
    """
    Configuration dataclass for outlier-x.

    Manages freshness rules, schema fields, null policies, and general settings.
    """

    # Data freshness rules (sport -> max age in hours)
    freshness_rules: Dict[str, int] = Field(
        default_factory=lambda: {sport: 24 for sport in SPORTS}
    )

    # Required schema fields in order
    schema_fields: List[str] = Field(
        default_factory=lambda: [
            "event_id",
            "sport",
            "event_date",
            "teams",
            "odds_provider",
            "odds",
            "line",
            "volume",
            "timestamp",
            "data_source",
        ]
    )

    # Null/nullable policies for each field
    null_policies: Dict[str, bool] = Field(
        default_factory=lambda: {
            "event_id": False,
            "sport": False,
            "event_date": False,
            "teams": False,
            "odds_provider": False,
            "odds": False,
            "line": True,
            "volume": False,
            "timestamp": False,
            "data_source": False,
        }
    )

    # Output configuration
    output_format: str = Field(default=DEFAULT_OUTPUT_FORMAT)
    output_dir: Path = Field(default=Path("data/processed"))

    # Processing configuration
    strict_mode: bool = Field(default=DEFAULT_STRICT_MODE)
    batch_size: int = Field(default=DEFAULT_BATCH_SIZE)
    log_level: str = Field(default=DEFAULT_LOG_LEVEL)
    log_dir: Path = Field(default=Path("logs"))

    # Source-specific configuration
    source_config: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True

    @validator("output_format")
    def validate_output_format(cls, v: str) -> str:
        """Validate output format is supported."""
        if v not in OUTPUT_FORMATS:
            raise ValueError(
                f"Invalid output format: {v}. Must be one of {OUTPUT_FORMATS}"
            )
        return v

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is supported."""
        if v not in LOG_LEVELS:
            raise ValueError(f"Invalid log level: {v}. Must be one of {LOG_LEVELS}")
        return v

    @validator("batch_size")
    def validate_batch_size(cls, v: int) -> int:
        """Validate batch size is positive."""
        if v <= 0:
            raise ValueError("batch_size must be positive")
        return v

    @validator("freshness_rules")
    def validate_freshness_rules(cls, v: Dict[str, int]) -> Dict[str, int]:
        """Validate freshness rules have positive hours."""
        for sport, hours in v.items():
            if hours <= 0:
                raise ValueError(f"Freshness rule for {sport} must be positive hours")
        return v

    @classmethod
    def from_yaml(cls, config_path: str) -> "Config":
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file

        Returns:
            Config instance

        Raises:
            ConfigurationError: If file not found or invalid YAML
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise ConfigurationError(f"Config file not found: {config_path}")

        try:
            with open(config_file, "r") as f:
                config_data = yaml.safe_load(f) or {}
            return cls(**config_data)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading config: {e}")

    @classmethod
    def from_env(cls) -> "Config":
        """
        Load configuration from environment variables with defaults.

        Returns:
            Config instance
        """
        config_path = os.getenv("OUTLIER_CONFIG_PATH")
        if config_path:
            return cls.from_yaml(config_path)

        # Build config from environment variables
        config_data = {}

        if log_level := os.getenv("OUTLIER_LOG_LEVEL"):
            config_data["log_level"] = log_level

        if strict_mode := os.getenv("OUTLIER_STRICT_MODE"):
            config_data["strict_mode"] = strict_mode.lower() == "true"

        if output_format := os.getenv("OUTLIER_OUTPUT_FORMAT"):
            config_data["output_format"] = output_format

        if output_dir := os.getenv("OUTLIER_OUTPUT_DIR"):
            config_data["output_dir"] = Path(output_dir)

        return cls(**config_data)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of config
        """
        data = self.dict()
        data["output_dir"] = str(data["output_dir"])
        data["log_dir"] = str(data["log_dir"])
        return data

    def to_yaml(self, output_path: str) -> None:
        """
        Save configuration to YAML file.

        Args:
            output_path: Path where YAML file will be saved

        Raises:
            ConfigurationError: If write operation fails
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w") as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False)
        except Exception as e:
            raise ConfigurationError(f"Error saving config: {e}")
