# outlier-x 📉📈

> **Your high-agency co-pilot for smarter DFS plays.**

Welcome to **outlier-x** — a Python-powered sports betting stats tracker and analyst that automates the research grind. Built for the culture, this tool stops you from making "donation picks" by finding real edge in the data. Whether you're grinding PrizePicks, Underdog, or Sleeper, outlier-x helps you build optimized slips by mixing high-upside "Demon" props with stabilizing "Anchors."

**⚠️ Disclaimer:** This is a data analysis tool. Not financial advice — just pure algorithmic heat. Use responsibly.

---

## 🎯 What It Does

outlier-x ingests data from **Outlier.bet exports** and **X/Twitter community consensus**, then runs it through a production-grade pipeline to:
- **Validate data quality** — No stale bread. The tool checks timestamps and refuses to cook with data >7 days old.
- **Normalize & standardize** — Converts messy CSV/JSON exports into clean, consistent formats.
- **Generate insights** — Builds 12-15 mixed-sport parlays automatically, ranked by confidence (Tier A/B/C).
- **Audit trail** — Tracks every transformation with timestamps and hashes for full transparency.

Think of it as your research assistant that never sleeps. It handles the boring stuff so you can focus on the plays.

---

## ✨ Features

### 🔄 **Freshness First**
- **24H Rule:** Data older than 24 hours triggers a warning. Data older than 7 days? The tool demands a refresh. No stale picks allowed.
- Automated timestamp checks keep your edge sharp.

### 🧠 **Platform Intelligence**
- Knows the difference between a PrizePicks "Reboot" (safe) and an Underdog "Ladder" (high upside).
- Sport-specific validation rules for football, basketball, baseball, and hockey.

### 😈 **Demon Mode**
- Automatically hunts for high-risk/high-reward props (Demons) and pairs them with stabilizers (Anchors).
- Balances your slips for optimal risk-reward.

### 📊 **Data Quality Reports**
- Generates validation reports with error breakdowns, field-level stats, and completeness metrics.
- Summary reports show record counts, transformations applied, and pipeline duration.

### 🔧 **Developer-Friendly**
- Type-safe Python codebase with comprehensive error handling.
- Modular architecture: ingest, normalize, validate, report.
- CLI-driven workflow with dry-run support.

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.9+** (Python 3.10+ recommended for best performance)
- pip package manager
- (Optional) Virtual environment for isolation

### Quick Install

```bash
# Clone the repo
git clone https://github.com/allsxxing/outlier-x.git
cd outlier-x

# (Recommended) Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root for API keys and settings:

```bash
# .env example
OUTLIER_API_KEY=your_outlier_key_here
TWITTER_API_KEY=your_twitter_key_here
GOOGLE_DRIVE_FOLDER_ID=your_drive_folder_id
OUTLIER_LOG_LEVEL=INFO
OUTLIER_OUTPUT_DIR=data/processed
```

*Note: API integration is optional. The tool works great with local exports too.*

---

## 💻 How to Use

### The Workflow

1. **Drop Your Data**  
   Put your Outlier.bet exports (`.json` or `.csv`) in the `data/raw/` folder or sync via Google Drive.

2. **Run the Pipeline**  
   Fire up the CLI to process your data:
   ```bash
   # Full pipeline: ingest → normalize → validate → report
   python -m src.main process --source json --path data/raw/outlier_export.json
   
   # Or run steps individually:
   python -m src.main ingest --source csv --path data/raw/props.csv --output data/processed/raw_data.json
   python -m src.main normalize --input data/processed/raw_data.json --output data/processed/normalized.json
   python -m src.main validate --input data/processed/normalized.json
   ```

3. **Review the Output**  
   Check the generated reports in `data/processed/`:
   - `final_data.json` — Your clean, validated dataset
   - `validation_report.txt` — Data quality breakdown
   - `summary_report.txt` — Pipeline stats and durations

4. **Build Your Slips**  
   Use the validated data to identify value plays and build your parlays. The tool ranks props by confidence tier (A/B/C).

### CLI Commands Reference

| Command     | Purpose                                    | Example                                                                 |
|-------------|--------------------------------------------|-------------------------------------------------------------------------|
| `process`   | Full pipeline (ingest → normalize → validate) | `python -m src.main process --source json --path data.json`             |
| `ingest`    | Load data from source                      | `python -m src.main ingest --source csv --path props.csv`               |
| `normalize` | Standardize data format                    | `python -m src.main normalize --input raw.json --output clean.json`     |
| `validate`  | Run data quality checks                    | `python -m src.main validate --input clean.json --strict`               |
| `report`    | Generate data quality report               | `python -m src.main report --input clean.json --output report.txt`      |

**Flags:**
- `--dry-run` — Preview changes without saving files
- `--strict` — Fail pipeline on any validation error
- `--output-dir` — Custom output directory (default: `data/processed`)

---

## 📈 Output Examples

### Validation Report
```
===== VALIDATION REPORT =====
Total Records: 1,245
Valid Records: 1,198 (96.2%)
Invalid Records: 47 (3.8%)

Top Errors by Field:
- event_date: 23 errors (invalid timestamp format)
- odds: 18 errors (below minimum threshold)
- volume: 6 errors (negative value)

✓ Overall Data Quality: GOOD
```

### Demon Parlay Output (Tier A)
```
🎰 TIER A PARLAY (5-Leg)

1. Anthony Edwards OVER 25.5 Points 😈
   → Books sleeping on his home splits (63% hit rate)

2. Bam Adebayo OVER 9.5 Rebounds ⚓
   → Anchor play: 78% hit rate vs. weak frontcourts

3. Luka Doncic OVER 8.5 Assists ⚓
   → Safe volume play in uptempo matchup

4. Tyrese Maxey OVER 3.5 Threes 😈
   → Elevated usage with Embiid out

5. Domantas Sabonis OVER 12.5 Rebounds ⚓
   → Board magnet averaging 14.2 last 10 games

💰 Suggested Unit: 1.5u | Expected Value: +12.3%
```

---

## 🛠 Development

### Code Quality Tools

```bash
# Linting
ruff check src tests

# Formatting
black src tests

# Type checking
mypy src

# Run tests
pytest

# Coverage report
pytest --cov=src --cov-report=html
```

### Project Structure

```
outlier-x/
├── src/
│   ├── config.py         # Configuration management
│   ├── ingest.py         # Data ingestion (CSV, JSON, API)
│   ├── normalize.py      # Data normalization engine
│   ├── validate.py       # Validation rules & reporting
│   ├── report.py         # Report generation
│   ├── main.py           # CLI entry point
│   └── utils/            # Shared utilities
├── tests/                # Test suite
├── data/
│   ├── raw/              # Input data
│   └── processed/        # Output data
├── requirements.txt      # Python dependencies
└── pyproject.toml        # Project configuration
```

---

## 🗺 Roadmap

- [ ] **More Sports:** Expand support to MMA, tennis, soccer
- [ ] **Live Data Feeds:** Real-time odds tracking and alerts
- [ ] **ML Models:** Predictive modeling for prop outcomes
- [ ] **Discord Bot:** Auto-post daily slips to Discord channels
- [ ] **Bankroll Tracker:** Monitor ROI and unit performance over time
- [ ] **API Endpoints:** RESTful API for programmatic access

---

## 🤝 Contributing

We welcome contributions from the community! Whether you're fixing bugs, adding features, or improving docs:

1. **Fork the repo** and create a feature branch (`git checkout -b feature/amazing-feature`)
2. **Make your changes** and ensure all tests pass (`pytest`)
3. **Lint your code** (`black src tests && ruff check src tests`)
4. **Commit with clear messages** (`git commit -m 'Add amazing feature'`)
5. **Push and open a PR** — Reference any related issues

**Pro Tip:** Check the project structure and coding standards in the Development section above.

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built for the sports betting community. Shoutout to:
- **Outlier.bet** for the data foundation
- The DFS grinders who inspired this project
- Contributors who help make it better

---

**Remember:** Data is your edge, but discipline is your bankroll saver. Good luck out there! 🎰

---

*Questions? Open an issue or reach out to the maintainers.*