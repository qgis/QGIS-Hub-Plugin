# Testing Guide for QGIS Hub Plugin

This guide explains how to run tests for the QGIS Hub Plugin, including solutions for common issues.

## Quick Reference

```bash
# Activate environment
source .venv/bin/activate

# Run unit tests only (fast, no QGIS required)
pytest tests/unit/ -v

# Run QGIS integration tests (requires QGIS, ~8-10 seconds)
pytest tests/qgis/ -v

# Run all tests
pytest tests/ -v

# Skip QGIS tests explicitly
pytest tests/ -v -m "not qgis"
```

## Test Structure

### Unit Tests (`tests/unit/`)
**Fast tests** that don't require QGIS. These tests use mocks for all external dependencies.

- ✅ **No QGIS installation needed** (most tests)
- ✅ **Fast execution** (milliseconds)
- ✅ **Run in CI/CD easily**
- Coverage: API client, resource items, utilities

**Files:**
- `test_api_client_mocked.py` - API with mocked network
- `test_resource_item.py` - Resource item creation (requires QGIS, skipped in CI if unavailable)
- `test_utilities.py` - Download and utility functions
- `test_plg_metadata.py` - Metadata parsing

**Note:** `test_resource_item.py` actually requires QGIS because it creates `ResourceItem` objects which inherit from Qt's `QStandardItem`. These tests are automatically skipped when QGIS is not available (e.g., in the unit tests CI job) and will run in the QGIS integration tests CI job instead.

### Integration Tests (`tests/qgis/`)
**Slower tests** that require a full QGIS environment. These test the actual plugin integration with QGIS.

- ⚠️ **Requires QGIS installation**
- ⚠️ **Slower execution** (~8-10 seconds total)
- ⚠️ **Requires display server** (X11 or Wayland)
- Coverage: Resource browser dialog, filtering, QGIS integration

**Files:**
- `test_filter_proxy.py` - MultiRoleFilterProxyModel
- `test_integration.py` - End-to-end workflows
- `test_api_client.py` - Real API calls (optional)
- `test_plg_preferences.py` - Settings structure

## Why Do Integration Tests Take Time?

Integration tests need to:
1. **Initialize QGIS** (~0.5-1 second first time)
2. **Load Qt/PyQt** libraries
3. **Create GUI widgets** (resource browser dialog)
4. **Process Qt events**

This is normal and expected! The tests aren't hanging - they're just doing real work.

## Common Issues and Solutions

### Issue 1: Tests Seem to Hang

**Symptom:** Tests take 8-10 seconds to start or complete

**Solution:** This is **normal** for QGIS tests. They need to:
- Initialize the QGIS application
- Load PyQGIS libraries
- Create Qt widgets

**What to do:** Be patient! The tests will complete. If they take more than 30 seconds, then there's a real issue.

### Issue 2: ModuleNotFoundError: No module named 'qgis'

**Symptom:**
```
ImportError: No module named 'qgis.core'
```

**Solution:** QGIS is not installed or not accessible

**Fix:**
```bash
# Check if QGIS is available
python -c "from qgis.core import QgsApplication; print('QGIS OK')"

# If not, ensure virtual environment has system packages
python -m venv .venv --system-site-packages

# Or install QGIS (Ubuntu)
sudo apt install qgis python3-qgis
```

### Issue 3: QXcbConnection: Could not connect to display

**Symptom:**
```
qt.qpa.xcb: could not connect to display
```

**Solution:** QGIS GUI needs a display server

**Fix Option 1 - Use existing display:**
```bash
export DISPLAY=:0
pytest tests/qgis/ -v
```

**Fix Option 2 - Use virtual display (headless):**
```bash
# Install Xvfb
sudo apt install xvfb

# Run with virtual display
xvfb-run pytest tests/qgis/ -v
```

### Issue 4: AttributeError in Integration Tests

**Symptom:**
```
AttributeError: 'ResourceBrowserDialog' object has no attribute 'model'
```

**Solution:** This was fixed! The correct attributes are:
- `dialog.resource_model` (not `dialog.model`)
- `dialog.proxy_model`

**Status:** ✅ Already fixed in the current tests

### Issue 5: Mock Not Working

**Symptom:** Real API is called instead of mock

**Solution:** Patch where the function is **used**, not where it's **defined**

**Wrong:**
```python
@patch("qgis_hub_plugin.core.api_client.get_all_resources")  # ❌
```

**Correct:**
```python
@patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")  # ✅
```

## Running Tests Efficiently

### Development Workflow

During development, run only fast unit tests:

```bash
# Fast feedback loop
pytest tests/unit/ -v

# With file watching (requires pytest-watch)
ptw tests/unit/ -- -v
```

Before committing, run all tests:

```bash
# Complete test suite
pytest tests/ -v
```

### CI/CD Workflow

For continuous integration, separate fast and slow tests:

```bash
# Fast CI step (unit tests)
pytest tests/unit/ -v --cov=qgis_hub_plugin

# Slow CI step (integration tests, optional)
xvfb-run pytest tests/qgis/ -v
```

## Test Markers

Tests are marked for selective execution:

```bash
# Run only QGIS tests
pytest -v -m qgis

# Skip QGIS tests
pytest -v -m "not qgis"

# Run only slow tests
pytest -v -m slow
```

## Coverage Reports

```bash
# Generate HTML coverage report
pytest tests/unit/ --cov=qgis_hub_plugin --cov-report=html

# View report
open htmlcov/index.html

# Generate terminal report
pytest tests/unit/ --cov=qgis_hub_plugin --cov-report=term
```

## Expected Test Times

| Test Suite | Tests | Time | QGIS Required |
|------------|-------|------|---------------|
| Unit Tests (no QGIS) | 27 | < 1s | ❌ No |
| Unit Tests (with QGIS) | 47 | ~7s | ⚠️ Partial (test_resource_item.py) |
| Integration Tests | 6 | ~8-10s | ✅ Yes |
| Filter Proxy Tests | 18 | ~2-3s | ✅ Yes |
| **Total** | **52+** | **~10-15s** | Partial |

**Note:** In CI, the unit tests job runs 27 tests (skips test_resource_item.py), and the QGIS job runs all QGIS-dependent tests including those from tests/unit/.

## Debugging Failed Tests

### Verbose Output

```bash
# Show full output
pytest tests/qgis/test_integration.py -v -s

# Show local variables on failure
pytest tests/qgis/test_integration.py -v -l

# Stop on first failure
pytest tests/qgis/test_integration.py -v -x
```

### Coverage Analysis

```bash
# See which lines aren't covered
pytest tests/unit/ --cov=qgis_hub_plugin --cov-report=term-missing
```

### Run Specific Test

```bash
# Run single test
pytest tests/qgis/test_integration.py::TestIntegration::test_resource_browser_with_empty_response -v

# Run test class
pytest tests/qgis/test_integration.py::TestIntegration -v
```

## Environment Variables

Useful environment variables for testing:

```bash
# Use virtual display
export QT_QPA_PLATFORM=offscreen

# Increase Qt logging
export QT_LOGGING_RULES="*.debug=true"

# Set display
export DISPLAY=:0
```

## Docker Testing (Advanced)

For consistent QGIS environment (same as CI):

```bash
# Pull QGIS image (same as CI uses)
docker pull qgis/qgis:release-3_34

# Run integration tests in container
docker run --rm -v $(pwd):/app -w /app \
  -e QT_QPA_PLATFORM=offscreen \
  -e PYTHONPATH=/usr/share/qgis/python/plugins:/usr/share/qgis/python \
  qgis/qgis:release-3_34 \
  bash -c "pip install -r requirements/testing.txt && pytest tests/qgis/ -v"

# Run all tests in container
docker run --rm -v $(pwd):/app -w /app \
  -e QT_QPA_PLATFORM=offscreen \
  qgis/qgis:release-3_34 \
  bash -c "pip install -r requirements/testing.txt && pytest tests/ -v"
```

## CI/CD Testing

The project uses GitHub Actions for automated testing:

### Workflow Jobs

**1. Unit Tests (Fast)**
- Runs on: Ubuntu Latest + Python 3.9
- Duration: ~30 seconds
- Command: `pytest tests/unit/ -v`
- No QGIS required (tests requiring QGIS are auto-skipped)
- Note: `test_resource_item.py` tests are skipped here (run in QGIS job instead)
- Uploads coverage to Codecov

**2. Integration Tests (QGIS)**
- Runs on: QGIS Docker container (`qgis/qgis:release-3_34`)
- Duration: ~1-2 minutes
- Command: `pytest tests/qgis/ -v -m qgis`
- Full QGIS environment
- Uploads coverage to Codecov

### Environment Setup

The CI uses the official QGIS Docker images:

```yaml
container:
  image: qgis/qgis:release-3_34  # QGIS LTS
  options: --user root

env:
  QT_QPA_PLATFORM: offscreen      # No display needed
  QGIS_PREFIX_PATH: /usr
  PYTHONPATH: /usr/share/qgis/python/plugins:/usr/share/qgis/python
```

### Triggers

Tests run automatically on:
- Push to `main` branch (when `**.py` files change)
- Pull requests to `main` branch (when `**.py` files change)

### View Test Results

Check test status:
1. Go to GitHub repository
2. Click "Actions" tab
3. View workflow runs
4. See detailed test logs

For more details, see [`.github/workflows/README.md`](../.github/workflows/README.md)

## Summary

✅ **Unit tests are fast** - Run them frequently during development

⚠️ **Integration tests are slower** - This is normal and expected

🔧 **Use markers** - Skip QGIS tests when not needed

📊 **Check coverage** - Aim for 80%+ on unit tests

🐛 **Debug with -v -s** - See full output when debugging

---

**Last Updated:** 2025-10-24

**Test Suite Version:** 1.0

**Total Tests:** 52+ across 8 files
