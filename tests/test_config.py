"""Tests for the config module."""

import os
from pathlib import Path

import pytest
import yaml

from src.config import Config
from src.utils.errors import ConfigurationError
from src.utils.constants import (
    DEFAULT_LOG_LEVEL,
    DEFAULT_BATCH_SIZE,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_STRICT_MODE,
)


@pytest.fixture
def valid_config_dict():
    """Return a valid configuration dictionary."""
    return {
        "freshness_rules": {
            "football": 24,
            "basketball": 12,
        },
        "output_format": "json",
        "log_level": "INFO",
        "batch_size": 1000,
        "strict_mode": False,
    }


@pytest.fixture
def valid_config_yaml(tmp_path, valid_config_dict):
    """Create a valid YAML configuration file."""
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(valid_config_dict, f)
    return config_file


@pytest.fixture
def invalid_yaml_file(tmp_path):
    """Create an invalid YAML file."""
    config_file = tmp_path / "invalid.yaml"
    with open(config_file, "w") as f:
        f.write("invalid: yaml: content: [")
    return config_file


class TestConfigDefaults:
    """Test Config default values."""

    def test_config_default_initialization(self):
        """Test Config initializes with defaults."""
        config = Config()
        assert config.output_format == DEFAULT_OUTPUT_FORMAT
        assert config.log_level == DEFAULT_LOG_LEVEL
        assert config.batch_size == DEFAULT_BATCH_SIZE
        assert config.strict_mode == DEFAULT_STRICT_MODE

    def test_config_default_freshness_rules(self):
        """Test default freshness rules are set."""
        config = Config()
        assert "football" in config.freshness_rules
        assert "basketball" in config.freshness_rules
        assert config.freshness_rules["football"] == 24

    def test_config_default_schema_fields(self):
        """Test default schema fields are set."""
        config = Config()
        assert "event_id" in config.schema_fields
        assert "sport" in config.schema_fields
        assert "volume" in config.schema_fields

    def test_config_default_null_policies(self):
        """Test default null policies are set."""
        config = Config()
        assert config.null_policies["event_id"] is False
        assert config.null_policies["line"] is True


class TestConfigValidators:
    """Test Config validators."""

    def test_validator_output_format_valid(self):
        """Test output_format validator accepts valid formats."""
        config = Config(output_format="json")
        assert config.output_format == "json"

        config = Config(output_format="csv")
        assert config.output_format == "csv"

        config = Config(output_format="parquet")
        assert config.output_format == "parquet"

    def test_validator_output_format_invalid(self):
        """Test output_format validator rejects invalid formats."""
        with pytest.raises(ValueError, match="Invalid output format"):
            Config(output_format="xml")

    def test_validator_log_level_valid(self):
        """Test log_level validator accepts valid levels."""
        config = Config(log_level="DEBUG")
        assert config.log_level == "DEBUG"

        config = Config(log_level="INFO")
        assert config.log_level == "INFO"

        config = Config(log_level="WARNING")
        assert config.log_level == "WARNING"

        config = Config(log_level="ERROR")
        assert config.log_level == "ERROR"

    def test_validator_log_level_invalid(self):
        """Test log_level validator rejects invalid levels."""
        with pytest.raises(ValueError, match="Invalid log level"):
            Config(log_level="INVALID")

    def test_validator_batch_size_valid(self):
        """Test batch_size validator accepts positive values."""
        config = Config(batch_size=100)
        assert config.batch_size == 100

        config = Config(batch_size=1)
        assert config.batch_size == 1

    def test_validator_batch_size_invalid(self):
        """Test batch_size validator rejects non-positive values."""
        with pytest.raises(ValueError, match="batch_size must be positive"):
            Config(batch_size=0)

        with pytest.raises(ValueError, match="batch_size must be positive"):
            Config(batch_size=-1)

    def test_validator_freshness_rules_valid(self):
        """Test freshness_rules validator accepts positive hours."""
        config = Config(freshness_rules={"football": 24, "basketball": 12})
        assert config.freshness_rules["football"] == 24

    def test_validator_freshness_rules_invalid(self):
        """Test freshness_rules validator rejects non-positive hours."""
        with pytest.raises(ValueError, match="must be positive hours"):
            Config(freshness_rules={"football": 0})

        with pytest.raises(ValueError, match="must be positive hours"):
            Config(freshness_rules={"football": -24})


class TestConfigFromYAML:
    """Test loading Config from YAML file."""

    def test_from_yaml_valid_file(self, valid_config_yaml):
        """Test loading config from valid YAML file."""
        config = Config.from_yaml(str(valid_config_yaml))
        assert config.output_format == "json"
        assert config.log_level == "INFO"
        assert config.batch_size == 1000

    def test_from_yaml_file_not_found(self):
        """Test loading config fails when file not found."""
        with pytest.raises(ConfigurationError, match="Config file not found"):
            Config.from_yaml("nonexistent.yaml")

    def test_from_yaml_invalid_yaml(self, invalid_yaml_file):
        """Test loading config fails with invalid YAML."""
        with pytest.raises(ConfigurationError, match="Invalid YAML"):
            Config.from_yaml(str(invalid_yaml_file))

    def test_from_yaml_empty_file(self, tmp_path):
        """Test loading config from empty YAML file uses defaults."""
        config_file = tmp_path / "empty.yaml"
        config_file.write_text("")

        config = Config.from_yaml(str(config_file))
        assert config.output_format == DEFAULT_OUTPUT_FORMAT

    def test_from_yaml_partial_config(self, tmp_path):
        """Test loading partial config merges with defaults."""
        config_file = tmp_path / "partial.yaml"
        with open(config_file, "w") as f:
            yaml.dump({"log_level": "DEBUG"}, f)

        config = Config.from_yaml(str(config_file))
        assert config.log_level == "DEBUG"
        assert config.output_format == DEFAULT_OUTPUT_FORMAT  # Default

    def test_from_yaml_invalid_values(self, tmp_path):
        """Test loading config fails with invalid values."""
        config_file = tmp_path / "invalid_values.yaml"
        with open(config_file, "w") as f:
            yaml.dump({"log_level": "INVALID_LEVEL"}, f)

        with pytest.raises(ConfigurationError):
            Config.from_yaml(str(config_file))


class TestConfigFromEnv:
    """Test loading Config from environment variables."""

    def test_from_env_no_vars(self):
        """Test loading config from env with no vars uses defaults."""
        config = Config.from_env()
        assert config.output_format == DEFAULT_OUTPUT_FORMAT
        assert config.log_level == DEFAULT_LOG_LEVEL

    def test_from_env_with_config_path(self, valid_config_yaml, monkeypatch):
        """Test loading config from env with config path."""
        monkeypatch.setenv("OUTLIER_CONFIG_PATH", str(valid_config_yaml))
        config = Config.from_env()
        assert config.output_format == "json"

    def test_from_env_log_level(self, monkeypatch):
        """Test loading log level from env."""
        monkeypatch.setenv("OUTLIER_LOG_LEVEL", "DEBUG")
        config = Config.from_env()
        assert config.log_level == "DEBUG"

    def test_from_env_strict_mode(self, monkeypatch):
        """Test loading strict mode from env."""
        monkeypatch.setenv("OUTLIER_STRICT_MODE", "true")
        config = Config.from_env()
        assert config.strict_mode is True

        monkeypatch.setenv("OUTLIER_STRICT_MODE", "false")
        config = Config.from_env()
        assert config.strict_mode is False

    def test_from_env_output_format(self, monkeypatch):
        """Test loading output format from env."""
        monkeypatch.setenv("OUTLIER_OUTPUT_FORMAT", "csv")
        config = Config.from_env()
        assert config.output_format == "csv"

    def test_from_env_output_dir(self, monkeypatch):
        """Test loading output dir from env."""
        monkeypatch.setenv("OUTLIER_OUTPUT_DIR", "/custom/output")
        config = Config.from_env()
        assert str(config.output_dir) == "/custom/output"

    def test_from_env_multiple_vars(self, monkeypatch):
        """Test loading multiple vars from env."""
        monkeypatch.setenv("OUTLIER_LOG_LEVEL", "WARNING")
        monkeypatch.setenv("OUTLIER_STRICT_MODE", "true")
        monkeypatch.setenv("OUTLIER_OUTPUT_FORMAT", "parquet")

        config = Config.from_env()
        assert config.log_level == "WARNING"
        assert config.strict_mode is True
        assert config.output_format == "parquet"


class TestConfigToDict:
    """Test converting Config to dictionary."""

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = Config(log_level="DEBUG", batch_size=500)
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict["log_level"] == "DEBUG"
        assert config_dict["batch_size"] == 500

    def test_to_dict_includes_all_fields(self):
        """Test to_dict includes all config fields."""
        config = Config()
        config_dict = config.to_dict()

        assert "freshness_rules" in config_dict
        assert "schema_fields" in config_dict
        assert "null_policies" in config_dict
        assert "output_format" in config_dict
        assert "log_level" in config_dict

    def test_to_dict_path_conversion(self):
        """Test to_dict converts Path objects to strings."""
        config = Config()
        config_dict = config.to_dict()

        # Paths should be converted to strings
        assert isinstance(config_dict["output_dir"], str)
        assert isinstance(config_dict["log_dir"], str)


class TestConfigToYAML:
    """Test exporting Config to YAML file."""

    def test_to_yaml_creates_file(self, tmp_path):
        """Test to_yaml creates a YAML file."""
        config = Config(log_level="DEBUG", batch_size=2000)
        output_file = tmp_path / "output_config.yaml"

        config.to_yaml(str(output_file))

        assert output_file.exists()

    def test_to_yaml_content_valid(self, tmp_path):
        """Test to_yaml creates valid YAML content."""
        config = Config(log_level="ERROR", output_format="csv")
        output_file = tmp_path / "output_config.yaml"

        config.to_yaml(str(output_file))

        # Load and verify
        with open(output_file, "r") as f:
            loaded_data = yaml.safe_load(f)

        assert loaded_data["log_level"] == "ERROR"
        assert loaded_data["output_format"] == "csv"

    def test_to_yaml_creates_parent_directories(self, tmp_path):
        """Test to_yaml creates parent directories if needed."""
        config = Config()
        output_file = tmp_path / "subdir" / "nested" / "config.yaml"

        config.to_yaml(str(output_file))

        assert output_file.exists()
        assert output_file.parent.exists()

    def test_to_yaml_roundtrip(self, tmp_path):
        """Test config can be saved and loaded back."""
        original_config = Config(
            log_level="WARNING",
            batch_size=750,
            output_format="parquet"
        )
        output_file = tmp_path / "config.yaml"

        # Save
        original_config.to_yaml(str(output_file))

        # Load
        loaded_config = Config.from_yaml(str(output_file))

        assert loaded_config.log_level == original_config.log_level
        assert loaded_config.batch_size == original_config.batch_size
        assert loaded_config.output_format == original_config.output_format

    def test_to_yaml_invalid_path(self):
        """Test to_yaml fails with invalid path."""
        config = Config()
        with pytest.raises(ConfigurationError, match="Error saving config"):
            config.to_yaml("/invalid/path/that/cannot/be/created/config.yaml")


class TestConfigIntegration:
    """Integration tests for Config."""

    def test_config_full_workflow(self, tmp_path):
        """Test complete config workflow: create, save, load, modify."""
        # Create config
        config1 = Config(log_level="DEBUG", batch_size=1500)

        # Save to YAML
        config_file = tmp_path / "config.yaml"
        config1.to_yaml(str(config_file))

        # Load from YAML
        config2 = Config.from_yaml(str(config_file))
        assert config2.log_level == "DEBUG"
        assert config2.batch_size == 1500

        # Convert to dict
        config_dict = config2.to_dict()
        assert config_dict["log_level"] == "DEBUG"

    def test_config_env_override(self, valid_config_yaml, monkeypatch):
        """Test environment variables override config file."""
        monkeypatch.setenv("OUTLIER_CONFIG_PATH", str(valid_config_yaml))
        config = Config.from_env()
        # Config file has INFO
        assert config.log_level == "INFO"

    def test_config_custom_freshness_rules(self):
        """Test custom freshness rules configuration."""
        custom_rules = {
            "football": 48,
            "basketball": 24,
            "baseball": 36,
        }
        config = Config(freshness_rules=custom_rules)
        assert config.freshness_rules["football"] == 48
        assert config.freshness_rules["baseball"] == 36


# TODO: Add tests for:
# - Schema fields validation
# - Null policies validation
# - Source-specific configuration
# - Configuration merging strategies
# - Environment variable precedence
# - Invalid type conversions
# - Complex nested configuration structures
