# AGENTS.md — Agent-First Development Guide

> This file is the **single source of truth** for any AI agent (Cursor, Devin, AutoGPT, OpenHands, etc.) working on this codebase.
> Read this file **in full** before making any changes.

---

## 1. Project Overview

**Name:** `hkjc-scrapers` — 香港赛马会 (HKJC) Horse Racing Scraper Toolkit

**Purpose:** A Python scraping toolkit that extracts horse racing data from the Hong Kong Jockey Club website (`racing.hkjc.com`). It includes three independent scraper modules for race results, race schedules, and horse information.

**Language:** Python 3.10+

**Primary Dependencies:** `requests`, `beautifulsoup4`, `lxml`

**Test Framework:** `pytest`, `pytest-cov`

---

## 2. Repository Structure

```
hkjc_horse_racing_scraper/
├── src/
│   └── hkjc_scrapers/                # Main package (importable as `hkjc_scrapers`)
│       ├── __init__.py                # Exports: RaceResultScraper, RaceScheduleScraper, HorseInfoScraper
│       ├── race_result_scraper.py     # RaceResultScraper — scrapes single race results
│       ├── race_schedule_scraper.py   # RaceScheduleScraper — scrapes race calendar/fixtures
│       └── horse_info_scraper.py      # HorseInfoScraper — scrapes individual horse profiles
├── test/
│   ├── __init__.py
│   ├── test_race_result_scraper.py
│   ├── test_race_schedule_scraper.py
│   └── test_horse_info_scraper.py
├── example_race_result.py             # Usage example: race result scraper
├── example_schedule.py                # Usage example: schedule scraper
├── example_horse_info.py              # Usage example: horse info scraper
├── setup.py                           # Package installation config
├── pytest.ini                         # Pytest config (testpaths, pythonpath, markers)
├── requirements.txt                   # All dependencies (runtime + test)
├── setup_venv.sh                      # macOS/Linux venv bootstrap
├── setup_venv.bat                     # Windows venv bootstrap
├── .gitignore
├── README.md                          # User-facing documentation (中文)
├── TESTING.md                         # Testing guide (中文)
└── AGENTS.md                          # ← You are here
```

---

## 3. Environment Setup

### Quick Start (MUST run before any code changes)

```bash
# 1. Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate    # macOS/Linux
# venv\Scripts\activate     # Windows

# 2. Install all dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Install package in dev mode (recommended)
pip install -e .
```

### Verify Setup

```bash
# Run full test suite — this MUST pass before and after any changes
pytest test/ -v
```

### Python Path

- The `pytest.ini` sets `pythonpath = src`, so `import hkjc_scrapers` works in tests.
- Example scripts manually add `src/` to `sys.path`.
- If installed via `pip install -e .`, the package is available globally in the venv.

---

## 4. Architecture & Key Patterns

### Module Design

Each scraper follows the **same pattern**:

1. **Class-based**: One class per scraper (`RaceResultScraper`, `RaceScheduleScraper`, `HorseInfoScraper`)
2. **Session-based HTTP**: Uses `requests.Session()` with consistent headers (User-Agent, Accept, Accept-Language for zh-HK)
3. **Main scrape method**: `scrape_race_result(url)`, `scrape_schedule(url)`, `scrape_horse_info(url)` — returns a `Dict`
4. **Private extraction helpers**: `_extract_*()` methods that parse `BeautifulSoup` objects
5. **Output methods**: `save_to_json(result, filename)` and `save_to_csv(result, filename)`
6. **Error handling**: Each scrape method wraps logic in try/except and returns empty dict `{}` on failure

### Data Flow

```
URL → requests.get() → BeautifulSoup(html, 'html.parser') → _extract_*() → Dict → JSON/CSV
```

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase` (e.g. `RaceResultScraper`)
- **Methods**: `snake_case` (public: `scrape_*`, `save_to_*`, `get_*`; private: `_extract_*`, `_parse_*`)
- **Tests**: `test_<module>.py` → `class Test<ClassName>` → `def test_<feature>()`
- **Docstrings**: Chinese (中文) docstrings throughout the codebase
- **Comments**: Chinese (中文)

### Public API (exported from `__init__.py`)

```python
from hkjc_scrapers import RaceResultScraper    # scrape_race_result(url) → Dict
from hkjc_scrapers import RaceScheduleScraper   # scrape_schedule(url?) → Dict
from hkjc_scrapers import HorseInfoScraper      # scrape_horse_info(url) → Dict
```

---

## 5. HKJC URL Formats (Domain Knowledge)

Agents must understand these URL patterns when constructing or validating scraper inputs:

| Scraper | URL Pattern | Key Params |
|---------|-------------|------------|
| Race Result | `https://racing.hkjc.com/zh-hk/local/information/localresults?racedate=YYYY/MM/DD&Racecourse=XX&RaceNo=N` | `racedate`, `Racecourse` (ST=沙田, HV=跑马地), `RaceNo` (1-12) |
| Schedule | `https://racing.hkjc.com/zh-hk/local/information/fixture?calyear=YYYY&calmonth=MM` | `calyear`, `calmonth` (01-12) |
| Horse Info | `https://racing.hkjc.com/zh-hk/local/information/horse?horseid=XXXXX&Option=1` | `horseid` (e.g. `HK_2020_E436`), `Option` |

---

## 6. Testing

### Configuration (`pytest.ini`)

- **Test directory**: `test/`
- **Python path**: `src/` (auto-added)
- **Markers**: `integration`, `unit`, `slow`
- **Default flags**: `-v --strict-markers --tb=short --disable-warnings`

### Commands

```bash
# Run all tests (ALWAYS do this before committing)
pytest

# Run tests for a specific scraper
pytest test/test_race_result_scraper.py -v
pytest test/test_race_schedule_scraper.py -v
pytest test/test_horse_info_scraper.py -v

# Run a specific test method
pytest test/test_horse_info_scraper.py::TestHorseInfoScraper::test_scraper_initialization -v

# Coverage report
pytest test/ --cov=src/hkjc_scrapers --cov-report=html

# Re-run only failed tests
pytest test/ --lf
```

### Test Patterns

- All tests use **mocked HTTP responses** via `unittest.mock.patch` — no real network calls
- Fixtures provide `scraper` instances and `sample_html` strings
- Test classes mirror source classes: `TestRaceResultScraper`, `TestRaceScheduleScraper`, `TestHorseInfoScraper`

### Test Expectations

- **All tests must pass** before any PR or commit
- New features **must** include corresponding tests
- Tests should mock network calls — never make real HTTP requests in tests

---

## 7. Coding Standards & Conventions

### MUST Follow

1. **Language**: All docstrings, comments, and user-facing strings in **中文 (Chinese)**
2. **Type hints**: Use `typing` module (`Dict`, `List`, `Optional`) for all public method signatures
3. **Encoding**: Always declare `# -*- coding: utf-8 -*-` at top of `.py` files
4. **Shebang**: Include `#!/usr/bin/env python3` at top of executable scripts
5. **Error handling**: Wrap network calls in try/except; log errors via `print()` and return empty structures
6. **Consistent headers**: All scrapers must use the same `requests.Session` headers pattern
7. **No hardcoded paths**: Use `os.path.join()` for file paths

### MUST NOT Do

1. **Do NOT** make real HTTP requests in tests — always mock
2. **Do NOT** commit `.csv` or `.json` output files (they are gitignored)
3. **Do NOT** store credentials or API keys in source code
4. **Do NOT** modify the public API in `__init__.py` without updating all example scripts
5. **Do NOT** change `pytest.ini` settings without verifying all tests still pass
6. **Do NOT** add dependencies without adding them to `requirements.txt`

---

## 8. Adding a New Scraper

When adding a new scraper module, follow this checklist:

1. **Create** `src/hkjc_scrapers/<new_scraper>.py`:
   - Follow the existing class pattern (Session, `scrape_*()`, `_extract_*()`, `save_to_json()`, `save_to_csv()`)
   - Include proper Chinese docstrings and type hints
2. **Export** the new class in `src/hkjc_scrapers/__init__.py`:
   - Add import and update `__all__`
3. **Create** `test/test_<new_scraper>.py`:
   - Use mocked HTML responses
   - Test initialization, extraction methods, save methods, and error handling
4. **Create** `example_<name>.py` in project root:
   - Demonstrate basic usage with `sys.path` setup
5. **Update** `README.md`:
   - Add new scraper to feature list, usage examples, URL format, and JSON structure sections
6. **Run** full test suite to ensure no regressions: `pytest`

---

## 9. Common Tasks for Agents

### Task: Fix a Broken Scraper

1. Identify which scraper is broken and the specific `_extract_*()` method
2. Examine the current HKJC page HTML structure (the website changes periodically)
3. Update the BeautifulSoup selectors in the relevant `_extract_*()` method
4. Update corresponding test HTML fixtures if the page structure has changed
5. Run `pytest test/test_<scraper>.py -v` to verify the fix
6. Run `pytest` to ensure no regressions

### Task: Add a New Data Field

1. Add extraction logic in the relevant `_extract_*()` method
2. Include the new field in the return dict
3. Update `save_to_csv()` if the field should appear in CSV output
4. Add test cases for the new field with appropriate mock HTML
5. Update README.md with the new field in the JSON structure documentation

### Task: Improve Error Handling

1. Identify the failure scenario
2. Add appropriate try/except blocks or input validation
3. Ensure graceful degradation (return partial data, not crash)
4. Add test cases covering the error scenario
5. Verify with `pytest`

---

## 10. Output Formats Reference

### Return Value Structure

All scraper `scrape_*()` methods return a `Dict`. On failure, they return `{}`.

| Scraper | Top-level Keys |
|---------|---------------|
| `RaceResultScraper` | `race_date`, `racecourse`, `race_no`, `race_info`, `horses`, `race_result`, `incident_reports`, `pedigree` |
| `RaceScheduleScraper` | `source_url`, `scraped_at`, `months`, `race_days`, `legend`, `notices` |
| `HorseInfoScraper` | `horse_id`, `source_url`, `scraped_at`, `basic_info`, `race_records`, `equipment_legend` |

### File Outputs

- **JSON**: Full structured data via `save_to_json(result, filename)`
- **CSV**: Tabular subset via `save_to_csv(result, filename)` — race result saves horse data, schedule saves race days, horse info saves race records

---

## 11. Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: hkjc_scrapers` | Run `pip install -e .` or ensure `src/` is in `PYTHONPATH` |
| Tests fail with import errors | Activate venv: `source venv/bin/activate` |
| Scraper returns empty dict | HKJC page structure may have changed; inspect HTML manually |
| `lxml` install fails | Install system deps: `brew install libxml2 libxslt` (macOS) or `apt-get install libxml2-dev` (Linux) |
| CSV/JSON files not tracked by git | This is intentional — output files are in `.gitignore` |

---

## 12. Version & Metadata

- **Current version**: `0.1.0` (defined in `__init__.py` and `setup.py`)
- **Python requirement**: `>=3.10`
- **Package name**: `hkjc-scrapers`
- **License**: MIT

---

*Last updated: 2026-02-08*

