# GitHub Actions Workflows

This directory contains CI/CD workflows for the QGIS Hub Plugin.

## Workflows

### 🎳 Tester (`tester.yml`)

Runs automated tests on every push and pull request.

**Jobs:**

1. **Unit Tests (No QGIS)** - Fast tests without QGIS dependencies
   - Runs on: Ubuntu Latest with Python 3.9
   - Duration: ~30 seconds
   - Tests: `tests/unit/` (28+ tests)
   - Coverage: Uploads to Codecov with `unit` flag

2. **Integration Tests (QGIS)** - Tests requiring QGIS
   - Runs on: QGIS Docker container (`qgis/qgis:release-3_34`)
   - Duration: ~1-2 minutes
   - Tests: `tests/qgis/` (24+ tests)
   - Coverage: Uploads to Codecov with `integration` flag
   - Environment:
     - `QT_QPA_PLATFORM=offscreen` - No display required
     - `QGIS_PREFIX_PATH=/usr` - QGIS installation path
     - `PYTHONPATH` - Includes QGIS Python modules

**Triggers:**
- Push to `main` branch (when `**.py` files change)
- Pull requests to `main` branch (when `**.py` files change)

### ✅ Linter (`linter.yml`)

Runs code quality checks with flake8.

**Jobs:**
- Python linting with flake8
- Checks syntax errors and undefined names
- Reports code statistics

**Triggers:**
- Push to `main` branch (when `**.py` files change)
- Pull requests to `main` branch (when `**.py` files change)

### 📖 Documentation (`documentation.yml`)

Builds and publishes Sphinx documentation to GitHub Pages.

**Jobs:**
- Build Sphinx documentation
- Deploy to GitHub Pages

### 🚀 Releaser (`releaser.yml`)

Packages and releases the plugin.

**Jobs:**
- Creates plugin package
- Publishes GitHub release
- (Optional) Uploads to QGIS Plugin Repository

## QGIS Docker Container

The integration tests use the official QGIS Docker images:

**Image:** `qgis/qgis:release-3_34`
- QGIS LTS version 3.34
- Includes PyQGIS and Qt libraries
- Pre-configured QGIS environment
- Python 3.x with QGIS bindings

**Why Docker?**
- ✅ Consistent QGIS environment
- ✅ No manual QGIS installation
- ✅ Faster CI execution
- ✅ Isolated from host system
- ✅ Multiple QGIS versions available

**Available Tags:**
- `release-3_34` - LTS version (recommended)
- `release-3_28` - Older LTS
- `latest` - Latest stable release

## Environment Variables

### Unit Tests
- `PYTHON_VERSION=3.9` - Python version to use
- `PROJECT_FOLDER=qgis_hub_plugin` - Main plugin folder

### Integration Tests
- `CI=true` - Running in CI environment
- `QT_QPA_PLATFORM=offscreen` - Qt runs without display
- `QGIS_PREFIX_PATH=/usr` - QGIS installation path
- `PYTHONPATH=/usr/share/qgis/python/plugins:/usr/share/qgis/python` - QGIS Python modules

## Test Markers

Tests are marked for selective execution:

```yaml
# Run only QGIS tests
pytest tests/qgis/ -v -m qgis

# Skip QGIS tests
pytest tests/ -v -m "not qgis"
```

## Coverage Reports

Coverage is uploaded to Codecov with separate flags:
- `unit` - Unit test coverage
- `integration` - Integration test coverage

Combined coverage provides complete picture of test coverage.

## Troubleshooting

### Issue: QGIS tests fail with display errors

**Solution:** Set `QT_QPA_PLATFORM=offscreen`
```yaml
env:
  QT_QPA_PLATFORM: offscreen
```

### Issue: QGIS Python not found

**Solution:** Ensure `PYTHONPATH` includes QGIS modules
```yaml
env:
  PYTHONPATH: /usr/share/qgis/python/plugins:/usr/share/qgis/python
```

### Issue: Permission denied in container

**Solution:** Run as root user
```yaml
container:
  image: qgis/qgis:release-3_34
  options: --user root
```

### Issue: Tests timeout

**Solution:** Increase timeout for QGIS initialization
```yaml
- name: Run QGIS tests
  timeout-minutes: 10
  run: pytest tests/qgis/ -v
```

## Local Testing

To test the CI setup locally using Docker:

```bash
# Pull QGIS image
docker pull qgis/qgis:release-3_34

# Run tests in container
docker run --rm -v $(pwd):/app -w /app \
  -e QT_QPA_PLATFORM=offscreen \
  -e PYTHONPATH=/usr/share/qgis/python/plugins:/usr/share/qgis/python \
  qgis/qgis:release-3_34 \
  bash -c "pip install -r requirements/testing.txt && pytest tests/qgis/ -v"
```

## Performance

| Job | Duration | Tests | Coverage |
|-----|----------|-------|----------|
| Unit Tests | ~30s | 28+ | Unit code |
| Integration Tests | ~1-2min | 24+ | Integration code |
| **Total** | **~2-3min** | **52+** | **Combined** |

## Best Practices

1. **Fast Feedback** - Unit tests run first (fastest)
2. **Parallel Execution** - Jobs run concurrently
3. **Fail Fast** - Stop on first failure for quick feedback
4. **Coverage Tracking** - Monitor test coverage trends
5. **Matrix Testing** - (Future) Test multiple QGIS/Python versions

## Future Improvements

- [ ] Matrix strategy for multiple QGIS versions
- [ ] Matrix strategy for multiple Python versions
- [ ] Artifact upload for test reports
- [ ] Automatic plugin validation
- [ ] Performance benchmarking
- [ ] Security scanning

---

**Last Updated:** 2025-10-24
