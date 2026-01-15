# Outlier-X API

Welcome to the **Outlier-X Repository**. This repository contains production-grade Python CLI and tools for **Outlier.bet** data ingestion, normalization, and validation. The following documentation will guide you through setup, usage, development practices, and deployment workflows.

---

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
  - [Quick Start Guide](#quick-start-guide)
  - [CLI Commands](#cli-commands)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

---

## Overview
The Outlier-X project serves as the backbone for data handling at **Outlier.bet**. It provides tools for seamless data ingestion, robust validation pipelines, and normalization routines to ensure data consistency.

---

## Quick Start

Get up and running in 3 minutes:

```bash
# Clone and navigate to repository
git clone https://github.com/allsxxing/outlier-x.git
cd outlier-x

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Try it out with sample data
outlier-x process --source json --path examples/sample_data.json --dry-run
```

That's it! You've just run the full data processing pipeline. Continue reading for detailed installation and usage instructions.

---
## Installation

### Option 1: Install as a Package (Recommended)

1. **Clone Repository**
   ```bash
   git clone https://github.com/allsxxing/outlier-x.git
   cd outlier-x
   ```

2. **Create Python Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Package**
   ```bash
   pip install -e .
   ```

After installation, you can use the `outlier-x` command directly:
```bash
outlier-x --help
```

### Option 2: Development Setup

If you want to contribute or run the CLI without installing:

1. **Clone Repository**
   ```bash
   git clone https://github.com/allsxxing/outlier-x.git
   cd outlier-x
   ```

2. **Create Python Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

Run CLI commands using Python module syntax:
```bash
python -m src.main --help
```

---

## Usage

### Quick Start Guide

The CLI provides several commands for processing sports betting data. Below are common workflows:

#### 1. Full Pipeline (Recommended for First-Time Users)
Process data end-to-end with a single command:
```bash
# Using installed package
outlier-x process --source json --path examples/sample_data.json

# Or using development setup
python -m src.main process --source json --path examples/sample_data.json
```

This command will:
- Ingest data from the source
- Normalize the data format
- Validate against schema
- Generate reports

#### 2. Individual Commands

**Ingest Data:**
```bash
outlier-x ingest --source json --path examples/sample_data.json --output data/raw.json
```

**Normalize Data:**
```bash
outlier-x normalize --input data/raw.json --output data/normalized.json
```

**Validate Data:**
```bash
outlier-x validate --input data/normalized.json --output data/validation_report.txt
```

**Generate Report:**
```bash
outlier-x report --input data/normalized.json --output data/quality_report.txt
```

> **Note:** Replace `outlier-x` with `python -m src.main` if using the development setup.

### CLI Commands

| Command         | Description                                          | Key Options                                    |
|-----------------|------------------------------------------------------|------------------------------------------------|
| `process`       | Run full pipeline: ingest → normalize → validate    | `--source`, `--path`, `--output-dir`, `--dry-run` |
| `ingest`        | Ingest data from a source (json, csv, api)          | `--source`, `--path`, `--output`, `--dry-run`  |
| `normalize`     | Normalize raw data to consistent format             | `--input`, `--output`, `--dry-run`             |
| `validate`      | Validate data against schema                        | `--input`, `--output`, `--strict`              |
| `report`        | Generate data quality report                        | `--input`, `--output`                          |

#### Command Options Explained

- `--source`: Type of data source (`json`, `csv`, or `api`)
- `--path`: File path for json/csv or URL for api sources
- `--input`: Input file path for processing
- `--output`: Output file path for results
- `--output-dir`: Directory for multiple output files (used with `process`)
- `--dry-run`: Preview operations without saving (useful for testing)
- `--strict`: Fail if validation errors are found

### Examples with Sample Data

Try these commands with the provided example files:

```bash
# Test with JSON data
outlier-x process --source json --path examples/sample_data.json --dry-run

# Test with CSV data
outlier-x process --source csv --path examples/sample_data.csv --dry-run

# Process and save results
outlier-x process --source json --path examples/sample_data.json --output-dir data/processed

# Validate with strict mode (fail on errors)
outlier-x ingest --source json --path examples/sample_data.json --output data/raw.json
outlier-x normalize --input data/raw.json --output data/normalized.json
outlier-x validate --input data/normalized.json --strict
```

---

## Development

### Code Quality Tools

1. **Linting**
   
   Check code quality (requires installing dev dependencies):
   ```bash
   pip install -e ".[dev]"
   flake8 src tests
   ```

2. **Code Formatting**
   
   Apply consistent formatting:
   ```bash
   black src tests
   ```

3. **Type Checking**
   
   Run static type checking:
   ```bash
   mypy src
   ```

### Running Tests

Tests are written using the [pytest](https://docs.pytest.org) framework:

```bash
# Install dev dependencies if not already installed
pip install -e ".[dev]"

# Run all tests
pytest

# Run specific test file
pytest tests/test_ingest.py

# Run with coverage report
pytest --cov=src --cov-report=html
```

### Project Structure

```
outlier-x/
├── src/
│   ├── main.py          # CLI entry point
│   ├── config.py        # Configuration management
│   ├── ingest.py        # Data ingestion logic
│   ├── normalize.py     # Data normalization
│   ├── validate.py      # Data validation
│   ├── report.py        # Report generation
│   └── utils/           # Utility modules
├── tests/               # Test suite
├── examples/            # Example data files
├── pyproject.toml       # Project configuration
└── README.md            # This file
```

---
## Testing
Tests are written using the [pytest](https://docs.pytest.org) framework. The test suite includes:

- **Unit tests** for individual components
- **Integration tests** for complete workflows
- **Fixtures** with sample data in `tests/fixtures/`

Run tests with various options:

```bash
# Run all tests with output
pytest -v

# Run specific test categories
pytest tests/test_ingest.py -v
pytest tests/test_normalize.py -v
pytest tests/test_validate.py -v

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing

# View HTML coverage report
open htmlcov/index.html  # On macOS
# or
xdg-open htmlcov/index.html  # On Linux
```

---
## Deployment
Deployment for Outlier-X tools can occur on any Python-compatible server. Optionally, containerize it using Docker for simplified scaling and portability.

1. **Build Docker Image**
   ```bash
   docker build -t outlier-x:latest .
   ```

2. **Run Docker Container**
   ```bash
   docker run --rm -it outlier-x:latest
   ```

---

## Contributing

1. Fork the repository and create feature or bugfix branches.
2. Ensure all changes pass linting and tests before creating a pull request.
3. Reference issues in commits and PRs wherever applicable.

Thank you for contributing to Outlier-X!

---

## Troubleshooting

### Common Issues

**Issue: `ModuleNotFoundError: No module named 'src'`**
- **Solution**: Make sure you've installed the package with `pip install -e .` or use `python -m src.main` instead of `outlier-x`

**Issue: `outlier-x: command not found`**
- **Solution**: Ensure you've activated your virtual environment and installed the package with `pip install -e .`

**Issue: Validation errors after normalization**
- **Expected behavior**: The normalization process converts data formats (e.g., timestamps), which may not match the validation schema. This helps identify data quality issues.

**Issue: NumPy/PyArrow compatibility warnings**
- **Solution**: These warnings don't affect functionality. To suppress them, you can downgrade NumPy: `pip install "numpy<2"`

### Getting Help

- Check the example data in `examples/` directory to understand the expected data format
- Run any command with `--help` to see available options: `outlier-x <command> --help`
- Review test files in `tests/` for usage examples
- Open an issue on GitHub for bugs or feature requests

---

## Data Format Requirements

### Input Data Format

The CLI expects sports betting data with the following fields:

| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| `event_id`      | string | Yes      | Unique identifier for the event                  |
| `sport`         | string | Yes      | Sport type (football, basketball, baseball, hockey) |
| `event_date`    | string | Yes      | Event date (YYYY-MM-DD HH:MM:SS)                |
| `teams`         | string | Yes      | Team names                                       |
| `odds_provider` | string | Yes      | Source of odds data                              |
| `odds`          | dict   | Yes      | Odds values (home/away/draw)                     |
| `line`          | float  | No       | Betting line (nullable)                          |
| `volume`        | int    | Yes      | Betting volume                                   |
| `timestamp`     | string | Yes      | Data timestamp (YYYY-MM-DD HH:MM:SS)            |
| `data_source`   | string | Yes      | Source of the data                               |

**Note on CSV Format**: When using CSV files, complex data like the `odds` field (which is a dictionary/JSON object) should be represented as a JSON string with properly escaped double-quotes (e.g., `"{""home"": 1.85}"`). See `examples/sample_data.csv` for a working example.

See `examples/sample_data.json` and `examples/sample_data.csv` for working examples.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.