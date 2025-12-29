# Outlier.bet Ingest Protocol Specification

## Project Overview

Build a production-grade Python CLI tool for sports betting data ingestion, normalization, and validation. This tool processes raw betting data from multiple sources, standardizes it to a unified schema, validates data quality, and generates comprehensive reports.

## 1. Project Structure

```
outlier-x/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── ingest.py              # Data ingestion module
│   ├── normalize.py           # Data normalization
│   ├── validate.py            # Data validation
│   ├── report.py              # Report generation
│   ├── main.py                # CLI entry point
│   └── utils/
│       ├── __init__.py
│       ├── constants.py       # Constants and enums
│       ├── errors.py          # Custom exceptions
│       ├── logger.py          # Logging configuration
│       └── decorators.py      # Utility decorators
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_ingest.py
│   ├── test_normalize.py
│   ├── test_validate.py
│   ├── test_report.py
│   ├── test_main.py
│   └── fixtures/
│       ├── __init__.py
│       ├── sample_data.json
│       ├── expected_output.json
│       └── schema.json
├── data/
│   ├── raw/                   # Raw input data
│   └── processed/             # Processed output data
├── logs/                       # Application logs
├── docs/
│   ├── API.md
│   ├── USAGE.md
│   └── ARCHITECTURE.md
├── requirements.txt
├── pyproject.toml
├── setup.py
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
└── Makefile
```

## 2. Core Configuration (config.py)

### Config Dataclass
- `freshness_rules`: Dict mapping sport -> max age (hours)
- `schema_fields`: Ordered list of required fields
- `null_policies`: Dict mapping field -> nullable boolean
- `output_format`: str (json, csv, parquet)
- `strict_mode`: bool (fail on any validation error)
- `log_level`: str (DEBUG, INFO, WARNING, ERROR)
- `batch_size`: int (records per batch)
- `source_config`: Dict of source-specific settings

### Environment Variables
- `OUTLIER_CONFIG_PATH`: Path to config file
- `OUTLIER_LOG_LEVEL`: Override log level
- `OUTLIER_STRICT_MODE`: Override strict mode
- `OUTLIER_OUTPUT_DIR`: Output directory

## 3. Data Ingestion Module (ingest.py)

### DataSource (ABC)
- `abstract fetch() -> List[Dict[str, Any]]`
- `abstract validate_connection() -> bool`

### Implementations
- `JSONSource(DataSource)`: Reads JSON files
- `CSVSource(DataSource)`: Reads CSV files
- `APISource(DataSource)`: Fetches from HTTP endpoints
- `DatabaseSource(DataSource)`: Queries databases

### Ingest Manager
- `load_from_source(source: DataSource, **kwargs) -> DataFrame`
- `merge_sources(sources: List[DataSource]) -> DataFrame`
- `deduplicate(df: DataFrame, key: str) -> DataFrame`

## 4. Data Normalization Module (normalize.py)

### NormalizationEngine
- `normalize_field(value: Any, field_name: str, rules: Dict) -> Any`
- `normalize_row(row: Dict, schema: Dict) -> Dict`
- `normalize_dataframe(df: DataFrame, schema: Dict) -> DataFrame`

### Field Transformations
- `normalize_timestamp(value: Any, format: str = "%Y-%m-%d %H:%M:%S") -> datetime`
- `normalize_numeric(value: Any, decimal_places: int = 2) -> float`
- `normalize_string(value: Any, case: str = "lower") -> str`
- `normalize_boolean(value: Any) -> bool`
- `normalize_currency(value: Any, currency: str = "USD") -> float`
- `normalize_odds(value: Any, format: str = "decimal") -> float`

## 5. Data Validation Module (validate.py)

### ValidationEngine
- `validate_field(value: Any, field_name: str, rules: Dict) -> ValidationResult`
- `validate_row(row: Dict, schema: Dict) -> ValidationResult`
- `validate_dataframe(df: DataFrame, schema: Dict) -> ValidationReport`

### ValidationRule Types
- `required`: Field must not be null
- `type`: Field must match specified type
- `min_value` / `max_value`: Numeric bounds
- `min_length` / `max_length`: String length
- `pattern`: Regex matching
- `enum`: Value in allowed set
- `custom`: Custom validation function
- `business_rule`: Domain-specific validation

### ValidationResult
- `is_valid: bool`
- `errors: List[str]`
- `warnings: List[str]`
- `field_name: str`
- `value: Any`

### ValidationReport
- `total_records: int`
- `valid_records: int`
- `invalid_records: int`
- `warnings: List[str]`
- `errors_by_field: Dict[str, int]`
- `error_samples: List[Dict]`

## 6. Report Generation Module (report.py)

### ReportGenerator
- `generate_summary_report(data: DataFrame, stats: Dict) -> str`
- `generate_validation_report(validation_result: ValidationReport) -> str`
- `generate_data_quality_report(df: DataFrame) -> str`
- `export_report(report: str, format: str, path: str) -> None`

### Report Types
- Summary Report: Record counts, transformations applied, durations
- Validation Report: Error/warning breakdown, field-level stats
- Data Quality Report: Completeness, uniqueness, consistency metrics
- Executive Report: High-level overview for stakeholders

## 7. CLI Entry Point (main.py)

### Commands
- `ingest`: Fetch and load data from source
- `normalize`: Apply normalization rules
- `validate`: Run validation checks
- `process`: Full pipeline (ingest → normalize → validate)
- `report`: Generate reports from processed data
- `config`: Manage configuration

### Arguments
- `--source`: Data source identifier
- `--config`: Config file path
- `--output-dir`: Output directory
- `--format`: Output format (json, csv, parquet)
- `--strict`: Enable strict validation mode
- `--dry-run`: Preview changes without persisting
- `--parallel`: Enable parallel processing
- `--workers`: Number of worker processes

## 8. Error Handling Patterns

### Custom Exceptions Hierarchy
```
OutlierException
├── ConfigurationError
├── IngestionError
├── NormalizationError
├── ValidationError
├── ReportError
└── CLIError
```

### Error Handling Strategy
- Use typed exceptions for specific failures
- Implement retry logic for transient errors
- Log full context (timestamp, operation, input, error)
- Provide actionable error messages
- Collect all errors in batch mode, fail fast in strict mode

## 9. Testing Requirements

### Unit Tests
- Test each module function independently
- Use pytest fixtures for sample data
- Mock external dependencies (APIs, databases)
- Achieve 85%+ code coverage
- Test both happy paths and error cases

### Integration Tests
- Test full pipeline end-to-end
- Use sample data files from fixtures/
- Verify output matches expected schemas
- Test configuration loading and validation

### Test Organization
```
tests/
├── fixtures/          # Test data
├── unit/             # Unit tests
├── integration/      # Integration tests
└── conftest.py       # Pytest configuration
```

## 10. Installation & Usage

### Installation
```bash
git clone https://github.com/allsxxing/outlier-x.git
cd outlier-x
pip install -e .
```

### Usage Examples
```bash
# Full pipeline
outlier process --source json_file --config config.json

# Individual steps
outlier ingest --source csv_file data.csv
outlier normalize --input raw_data.json
outlier validate --input normalized_data.json
outlier report --input validated_data.json --output-format pdf

# Dry run
outlier process --source api --dry-run --verbose
```

## 11. Dependencies

### Core Dependencies
- **pandas**: Data manipulation and analysis
- **pydantic**: Data validation and configuration
- **click**: CLI framework
- **pyyaml**: YAML configuration parsing
- **python-dotenv**: Environment variable management
- **requests**: HTTP client for API sources
- **sqlalchemy**: Database connectivity
- **pyarrow**: Parquet file support

### Development Dependencies
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Static type checking
- **sphinx**: Documentation generation

## 12. Technical Stack Specifications

### Python Version
- Minimum: Python 3.9
- Target: Python 3.11+

### Code Standards
- Type hints on all functions
- Docstrings for all public APIs (Google style)
- PEP 8 compliance
- Black formatting (line length: 100)
- Mypy strict mode type checking

### Logging
- Structured logging with context
- Log rotation (daily, max 7 files)
- Different handlers for console and file
- Colorized console output for development

### Configuration Management
- YAML-based configuration files
- Environment variable overrides
- Validated configuration on startup
- Schema versioning for backward compatibility

## 13. Data Schema Definition

### Standard Betting Record Schema
```json
{
  "event_id": {"type": "string", "required": true},
  "sport": {"type": "string", "enum": ["football", "basketball", "baseball", "hockey"], "required": true},
  "event_date": {"type": "datetime", "required": true},
  "teams": {"type": "array", "length": 2, "required": true},
  "odds_provider": {"type": "string", "required": true},
  "odds": {
    "type": "object",
    "properties": {
      "team_a": {"type": "float", "min": 1.0, "required": true},
      "team_b": {"type": "float", "min": 1.0, "required": true}
    }
  },
  "line": {"type": "float", "nullable": true},
  "volume": {"type": "integer", "min": 0, "required": true},
  "timestamp": {"type": "datetime", "required": true},
  "data_source": {"type": "string", "required": true}
}
```

## 14. Function Signatures

### Key Function Signatures with Type Hints

```python
# config.py
class Config:
    freshness_rules: Dict[str, int]
    schema_fields: List[str]
    null_policies: Dict[str, bool]
    output_format: str
    strict_mode: bool
    log_level: str
    batch_size: int
    source_config: Dict[str, Any]

# ingest.py
def fetch_data(source: DataSource, **kwargs) -> pd.DataFrame: ...
def merge_sources(sources: List[DataSource]) -> pd.DataFrame: ...
def deduplicate(df: pd.DataFrame, key: str) -> pd.DataFrame: ...

# normalize.py
def normalize_field(value: Any, field_name: str, rules: Dict) -> Any: ...
def normalize_dataframe(df: pd.DataFrame, schema: Dict) -> pd.DataFrame: ...

# validate.py
def validate_field(value: Any, field_name: str, rules: Dict) -> ValidationResult: ...
def validate_dataframe(df: pd.DataFrame, schema: Dict) -> ValidationReport: ...

# report.py
def generate_summary_report(data: pd.DataFrame) -> str: ...
def generate_validation_report(result: ValidationReport) -> str: ...
def export_report(report: str, format: str, path: str) -> None: ...
```

## 15. Deployment Considerations

### CLI as Installable Package
- Use `setup.py` with entry_points for CLI command
- Version management with semantic versioning
- Package distribution via PyPI
- Docker support (optional Dockerfile included)

### Production Readiness
- Comprehensive error handling and logging
- Data validation before processing
- Checkpoint/resume capability for large datasets
- Performance optimization with batching
- Monitoring and observability hooks

## 16. Performance Requirements

### Benchmark Targets
- Ingest 1M records: < 30 seconds
- Normalize 1M records: < 60 seconds
- Validate 1M records: < 45 seconds
- Full pipeline 1M records: < 3 minutes
- Memory usage: < 2GB for 1M records

### Optimization Strategies
- Use vectorized operations in pandas
- Implement batch processing for validation
- Parallel processing support
- Lazy evaluation where possible
- Streaming for large files

## 17. Documentation Requirements

### Inline Documentation
- Module-level docstrings
- Function docstrings (Google style)
- Type hints on all functions
- Complex logic comments

### User Documentation
- README with quick start
- API documentation (generated from docstrings)
- Architecture and design decisions
- Configuration reference
- Troubleshooting guide
- Examples and use cases
