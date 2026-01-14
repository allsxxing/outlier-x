# Test Implementation Roadmap

**Project:** Outlier-X Test Coverage Improvement
**Start Date:** 2026-01-14
**Target:** 85%+ coverage from current 47%
**Duration:** 4 weeks

---

## Quick Reference

- 📋 **Current State:** 59 tests, 47% coverage
- 🎯 **Target State:** ~130 tests, 85%+ coverage
- 📊 **Progress Tracking:** Update this document as tests are completed
- 🚀 **Priority:** Start with Phase 1 (Critical gaps)

---

## Phase 1: Critical Coverage (Week 1)

**Goal:** Achieve 60% coverage by filling 0% coverage gaps
**Estimated Effort:** 20-25 hours
**Impact:** +13% coverage

### test_main.py - CLI Integration Tests

**File:** `tests/test_main.py` ✅ Skeleton created
**Priority:** 🔴 CRITICAL
**Coverage Impact:** +8%

#### Basic CLI Tests
- [ ] `test_cli_help` - Verify help text displays
- [ ] `test_cli_group_exists` - Verify CLI group configuration

#### Ingest Command
- [ ] `test_ingest_json_success` - JSON file ingestion
- [ ] `test_ingest_csv_success` - CSV file ingestion
- [ ] `test_ingest_api_success` - API endpoint ingestion (with mocking)
- [ ] `test_ingest_dry_run` - Dry run flag functionality
- [ ] `test_ingest_missing_path` - Error on missing path
- [ ] `test_ingest_invalid_source` - Error on invalid source type
- [ ] `test_ingest_file_not_found` - Error on missing file

#### Normalize Command
- [ ] `test_normalize_success` - Successful normalization
- [ ] `test_normalize_dry_run` - Dry run flag
- [ ] `test_normalize_missing_input` - Error handling
- [ ] `test_normalize_file_not_found` - File not found error

#### Validate Command
- [ ] `test_validate_success` - Successful validation
- [ ] `test_validate_strict_mode` - Strict mode behavior
- [ ] `test_validate_missing_input` - Error handling

#### Process Command
- [ ] `test_process_full_pipeline` - Complete pipeline execution
- [ ] `test_process_dry_run` - Dry run mode
- [ ] `test_process_strict_mode` - Strict mode with failures

#### Report Command
- [ ] `test_report_generation` - Report generation
- [ ] `test_report_missing_input` - Error handling

**Total:** 19 tests

---

### test_report.py - Report Generation Tests

**File:** `tests/test_report.py` ✅ Skeleton created
**Priority:** 🔴 CRITICAL
**Coverage Impact:** +5%

#### Summary Report Tests
- [ ] `test_generate_summary_report_basic` - Basic summary
- [ ] `test_generate_summary_report_with_stats` - With additional stats
- [ ] `test_generate_summary_report_empty_dataframe` - Empty data
- [ ] `test_generate_summary_report_zero_duration` - Zero duration edge case

#### Validation Report Tests
- [ ] `test_generate_validation_report_basic` - Basic validation report
- [ ] `test_generate_validation_report_includes_validity_rate` - Validity percentage
- [ ] `test_generate_validation_report_includes_errors_by_field` - Error breakdown
- [ ] `test_generate_validation_report_no_errors` - No errors case

#### Data Quality Report Tests
- [ ] `test_generate_data_quality_report_basic` - Basic quality report
- [ ] `test_generate_data_quality_report_includes_completeness` - Completeness metrics
- [ ] `test_generate_data_quality_report_with_nulls` - Null value handling

#### Export Tests
- [ ] `test_export_report_txt` - Export to text file
- [ ] `test_export_report_creates_directories` - Directory creation
- [ ] `test_export_report_overwrites_existing` - File overwriting

**Total:** 14 tests

---

## Phase 2: Important Coverage (Week 2)

**Goal:** Achieve 70% coverage with config and utilities
**Estimated Effort:** 15-20 hours
**Impact:** +10% coverage

### test_config.py - Configuration Tests

**File:** `tests/test_config.py` ✅ Skeleton created
**Priority:** 🟡 HIGH
**Coverage Impact:** +6%

#### Default Values Tests
- [ ] `test_config_default_initialization` - Default values
- [ ] `test_config_default_freshness_rules` - Default freshness
- [ ] `test_config_default_schema_fields` - Default schema
- [ ] `test_config_default_null_policies` - Default policies

#### Validator Tests
- [ ] `test_validator_output_format_valid` - Valid formats
- [ ] `test_validator_output_format_invalid` - Invalid format error
- [ ] `test_validator_log_level_valid` - Valid log levels
- [ ] `test_validator_log_level_invalid` - Invalid level error
- [ ] `test_validator_batch_size_valid` - Valid batch sizes
- [ ] `test_validator_batch_size_invalid` - Invalid size error
- [ ] `test_validator_freshness_rules_valid` - Valid rules
- [ ] `test_validator_freshness_rules_invalid` - Invalid rules error

#### YAML Loading Tests
- [ ] `test_from_yaml_valid_file` - Load valid YAML
- [ ] `test_from_yaml_file_not_found` - File not found error
- [ ] `test_from_yaml_invalid_yaml` - Invalid YAML error
- [ ] `test_from_yaml_empty_file` - Empty file handling
- [ ] `test_from_yaml_partial_config` - Partial config merge

#### Environment Variable Tests
- [ ] `test_from_env_no_vars` - No vars (defaults)
- [ ] `test_from_env_with_config_path` - Config path override
- [ ] `test_from_env_log_level` - Log level from env
- [ ] `test_from_env_strict_mode` - Strict mode from env
- [ ] `test_from_env_output_format` - Output format from env
- [ ] `test_from_env_multiple_vars` - Multiple vars

#### Export Tests
- [ ] `test_to_dict` - Convert to dictionary
- [ ] `test_to_yaml_creates_file` - Create YAML file
- [ ] `test_to_yaml_content_valid` - Valid YAML content
- [ ] `test_to_yaml_roundtrip` - Save and load back

**Total:** 26 tests

---

### test_decorators.py - Decorator Tests

**File:** `tests/test_decorators.py` ✅ Skeleton created
**Priority:** 🟢 MEDIUM
**Coverage Impact:** +3%

#### Timer Decorator Tests
- [ ] `test_timer_basic_functionality` - Basic timing
- [ ] `test_timer_with_arguments` - With function args
- [ ] `test_timer_measures_time_accurately` - Time accuracy
- [ ] `test_timer_preserves_function_name` - Metadata preservation
- [ ] `test_timer_with_return_values` - Return value handling

#### Retry Decorator Tests
- [ ] `test_retry_success_on_first_attempt` - No retries needed
- [ ] `test_retry_success_on_second_attempt` - One retry
- [ ] `test_retry_all_attempts_fail` - All retries fail
- [ ] `test_retry_with_custom_attempts` - Custom max attempts
- [ ] `test_retry_exponential_backoff` - Backoff timing
- [ ] `test_retry_with_different_exceptions` - Various exceptions
- [ ] `test_retry_preserves_function_name` - Metadata preservation

**Total:** 12 tests

---

## Phase 3: Enhancement (Week 3)

**Goal:** Achieve 80% coverage by expanding existing tests
**Estimated Effort:** 15-20 hours
**Impact:** +10% coverage

### Expand test_normalize.py

**File:** `tests/test_normalize.py`
**Priority:** 🟢 MEDIUM
**Coverage Impact:** +4%

#### New Tests to Add
- [ ] `test_normalize_timestamp_unix_int` - Unix timestamp (int)
- [ ] `test_normalize_timestamp_unix_float` - Unix timestamp (float)
- [ ] `test_normalize_timestamp_unsupported_type` - Unsupported type error
- [ ] `test_normalize_field_timestamp_type` - Field normalization (timestamp)
- [ ] `test_normalize_field_numeric_type` - Field normalization (numeric)
- [ ] `test_normalize_field_boolean_type` - Field normalization (boolean)
- [ ] `test_normalize_field_currency_type` - Field normalization (currency)
- [ ] `test_normalize_field_odds_type` - Field normalization (odds)
- [ ] `test_normalize_field_string_type` - Field normalization (string)
- [ ] `test_normalize_field_error_handling` - Field error handling
- [ ] `test_normalize_row` - Row normalization
- [ ] `test_normalize_row_error_handling` - Row error handling
- [ ] `test_normalize_dataframe` - DataFrame normalization
- [ ] `test_normalize_dataframe_empty` - Empty DataFrame
- [ ] `test_normalize_dataframe_error_handling` - DataFrame errors

**Total:** 15 tests

---

### Expand test_validate.py

**File:** `tests/test_validate.py`
**Priority:** 🟢 MEDIUM
**Coverage Impact:** +4%

#### New Tests to Add
- [ ] `test_validate_pattern_valid` - Valid pattern match
- [ ] `test_validate_pattern_invalid` - Invalid pattern
- [ ] `test_validate_pattern_none_value` - None value skipped
- [ ] `test_validate_pattern_error` - Pattern validation error
- [ ] `test_validate_custom_valid` - Custom validator success
- [ ] `test_validate_custom_invalid` - Custom validator failure
- [ ] `test_validate_custom_exception` - Custom validator exception
- [ ] `test_validate_field_with_pattern` - Field validation with pattern
- [ ] `test_validate_field_with_custom` - Field validation with custom
- [ ] `test_validate_field_all_rules` - All rules combined
- [ ] `test_validate_field_error_accumulation` - Multiple errors
- [ ] `test_validate_row_all_fields` - Complete row validation
- [ ] `test_validate_dataframe_error_extraction` - Error field extraction

**Total:** 13 tests

---

### Expand test_ingest.py

**File:** `tests/test_ingest.py`
**Priority:** 🟢 MEDIUM
**Coverage Impact:** +2%

#### New Tests to Add
- [ ] `test_api_source_timeout` - API timeout handling
- [ ] `test_api_source_connection_error` - Connection error
- [ ] `test_csv_source_encoding` - Different CSV encodings
- [ ] `test_csv_source_malformed` - Malformed CSV handling
- [ ] `test_json_source_nested_objects` - Nested JSON objects
- [ ] `test_ingestion_manager_large_files` - Large file handling
- [ ] `test_merge_sources_empty_sources` - Empty source list
- [ ] `test_deduplicate_no_duplicates` - No duplicates case

**Total:** 8 tests

---

## Phase 4: Edge Cases & Integration (Week 4)

**Goal:** Achieve 85%+ coverage with edge cases and integration
**Estimated Effort:** 15-20 hours
**Impact:** +5%+ coverage

### Integration Tests

**File:** `tests/test_integration.py` (new)
**Priority:** 🟢 MEDIUM
**Coverage Impact:** +3%

- [ ] `test_full_pipeline_json_to_report` - Complete pipeline
- [ ] `test_full_pipeline_csv_to_report` - CSV pipeline
- [ ] `test_full_pipeline_with_errors` - Pipeline with errors
- [ ] `test_multi_source_ingestion` - Multiple sources
- [ ] `test_error_propagation` - Error flow through pipeline
- [ ] `test_pipeline_with_deduplication` - Deduplication in pipeline
- [ ] `test_concurrent_processing` - Concurrent operations
- [ ] `test_large_dataset_processing` - Large dataset (10k+ rows)

**Total:** 8 tests

---

### Edge Case Tests

**Files:** Various test files
**Priority:** 🟢 MEDIUM
**Coverage Impact:** +2%

#### Data Edge Cases
- [ ] Empty DataFrames in all modules
- [ ] Single-row DataFrames
- [ ] Very large DataFrames (100k+ rows)
- [ ] Unicode and special characters
- [ ] Malformed data in all formats

#### Error Edge Cases
- [ ] Network failures (API source)
- [ ] File permission errors
- [ ] Disk space issues
- [ ] Memory constraints
- [ ] Invalid configuration combinations

#### Performance Tests
- [ ] Large file ingestion performance
- [ ] Validation performance with complex schemas
- [ ] Report generation for large datasets
- [ ] Memory usage monitoring

**Total:** 15+ tests

---

## Progress Tracking

### Overall Progress

| Phase | Status | Tests Completed | Coverage Goal | Actual Coverage |
|-------|--------|----------------|---------------|-----------------|
| **Baseline** | ✅ Complete | 59 | 47% | 47% |
| **Phase 1** | 🔄 Skeleton | 0/33 | 60% | TBD |
| **Phase 2** | 🔄 Skeleton | 0/38 | 70% | TBD |
| **Phase 3** | ⏳ Planned | 0/36 | 80% | TBD |
| **Phase 4** | ⏳ Planned | 0/23+ | 85%+ | TBD |
| **TOTAL** | | 59/189+ | 85%+ | TBD |

---

## Implementation Guidelines

### Before Starting Each Phase

1. ✅ Review the phase objectives
2. ✅ Set up your development environment
3. ✅ Run current tests to ensure baseline: `pytest -v`
4. ✅ Generate coverage report: `pytest --cov=src --cov-report=html`

### During Implementation

1. **Work on one test file at a time**
2. **Follow TDD principles:**
   - Write test first
   - Run test (should fail)
   - Implement/fix code
   - Run test (should pass)
   - Refactor if needed

3. **After each test class:**
   ```bash
   pytest tests/test_<module>.py::TestClassName -v
   ```

4. **Check coverage after completing a file:**
   ```bash
   pytest --cov=src.<module> tests/test_<module>.py --cov-report=term-missing
   ```

### After Completing Each Phase

1. ✅ Run full test suite: `pytest -v`
2. ✅ Generate coverage report: `pytest --cov=src --cov-report=html`
3. ✅ Review coverage gaps: `open htmlcov/index.html`
4. ✅ Update progress tracking in this document
5. ✅ Commit changes with descriptive message
6. ✅ Update TEST_COVERAGE_ANALYSIS.md with new metrics

---

## Quick Commands Reference

### Run Tests
```bash
# All tests
pytest -v

# Specific file
pytest tests/test_main.py -v

# Specific test class
pytest tests/test_main.py::TestIngestCommand -v

# Specific test
pytest tests/test_main.py::TestIngestCommand::test_ingest_json_success -v
```

### Coverage Reports
```bash
# Terminal report
pytest --cov=src --cov-report=term-missing

# HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Fail under threshold
pytest --cov=src --cov-fail-under=80
```

### Useful Options
```bash
# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run only failed tests from last run
pytest --lf

# Show slowest tests
pytest --durations=10
```

---

## Notes & Tips

### General Testing Tips

1. **Use fixtures liberally** - Create reusable test data
2. **Parameterize similar tests** - Use `@pytest.mark.parametrize`
3. **Mock external dependencies** - Don't make real API calls or file I/O when avoidable
4. **Test edge cases** - Empty data, None values, extreme values
5. **Clear test names** - Test name should describe what's being tested
6. **One assertion per test** - Makes failures easier to debug
7. **Arrange-Act-Assert** - Structure tests clearly

### Common Pitfalls to Avoid

- ❌ Don't test implementation details
- ❌ Don't make tests depend on each other
- ❌ Don't use real file paths (use tmp_path fixture)
- ❌ Don't skip error path testing
- ❌ Don't forget to test edge cases
- ❌ Don't leave TODO comments without creating them

### When Stuck

1. **Check existing test patterns** - Look at test_ingest.py, test_validate.py
2. **Review pytest documentation** - https://docs.pytest.org
3. **Use pytest fixtures** - Leverage tmp_path, capsys, monkeypatch
4. **Run single test** - Debug one test at a time
5. **Check coverage gaps** - Use htmlcov report to find untested lines

---

## Milestone Celebrations 🎉

Track your achievements!

- [ ] 🎯 **60% Coverage** - Phase 1 complete! Critical gaps filled.
- [ ] 🎯 **70% Coverage** - Phase 2 complete! Config and utilities tested.
- [ ] 🎯 **80% Coverage** - Phase 3 complete! Enhanced test suite.
- [ ] 🎯 **85% Coverage** - Phase 4 complete! Production-ready coverage!
- [ ] 🎯 **90% Coverage** - Stretch goal! Exceptional coverage.

---

## Resources

- **pytest Documentation:** https://docs.pytest.org/
- **pytest-cov Documentation:** https://pytest-cov.readthedocs.io/
- **Click Testing:** https://click.palletsprojects.com/en/8.1.x/testing/
- **unittest.mock:** https://docs.python.org/3/library/unittest.mock.html
- **Test Coverage Analysis:** `docs/TEST_COVERAGE_ANALYSIS.md`

---

*Last Updated: 2026-01-14*
*Next Review: After Phase 1 completion*
