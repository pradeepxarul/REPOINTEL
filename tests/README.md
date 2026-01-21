# Tests Directory

This directory contains test scripts for validating the GitHub User Data Analyzer functionality.

## Test Scripts

### Core Functionality Tests
- `test_complete_response.py` - Validates all API response fields are present
- `test_fresh_dependency_analysis.py` - Tests dependency analysis with fresh GitHub API data

### Legacy/Deprecated Tests
- `test_dependency_analysis.py` - Tests with stored data (may not have dependency files)

## Running Tests

```bash
# Test complete API response
python tests/test_complete_response.py

# Test dependency analysis (fresh fetch)
python tests/test_fresh_dependency_analysis.py
```

## Notes
- Tests require valid GitHub App credentials in `.env`
- Fresh data tests make actual GitHub API calls
- Stored data tests use cached data from `src/db/`
