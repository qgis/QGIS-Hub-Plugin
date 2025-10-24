# Development Environment Setup

This guide explains how to set up your development environment for the QGIS Hub Plugin.

## Prerequisites

- Python 3.12+ installed
- Git installed
- QGIS installed (for system packages like PyQGIS)
- Ubuntu/Linux system (recommended)

## Quick Setup

The development environment has been pre-configured with a virtual environment. Follow these steps to activate and start developing:

### 1. Activate the Virtual Environment

```bash
# Navigate to the project directory
cd /home/ismailsunni/dev/python/QGIS-Hub-Plugin

# Activate the virtual environment
source .venv/bin/activate
```

You should see `(.venv)` prefix in your terminal prompt.

### 2. Verify Installation

```bash
# Check Python version
python --version
# Expected: Python 3.12.3

# Check installed tools
pytest --version      # Test framework
black --version       # Code formatter
flake8 --version      # Linter
pre-commit --version  # Git hooks
```

### 3. Start Developing

You're ready to code! The environment includes:

- ✅ **black** - Code formatter
- ✅ **isort** - Import sorter
- ✅ **flake8** - Code linter (with QGIS plugin)
- ✅ **pytest** - Testing framework
- ✅ **pre-commit** - Git hooks for automated checks

## Installed Packages

### Development Tools
```
black                 25.9.0    # Code formatter
isort                 5.13.2    # Import sorter
flake8                7.3.0     # Code linter
flake8-builtins       2.2.0     # Check for builtin shadowing
flake8-isort          6.1.2     # isort integration
flake8-qgis           1.0.0     # QGIS-specific linting
pre-commit            3.8.0     # Git hook framework
```

### Testing Tools
```
pytest                8.4.2     # Test framework
pytest-cov            4.1.0     # Coverage reporting
pytest-mock           3.15.1    # Enhanced mocking
```

## Common Development Commands

### Code Quality

```bash
# Format code with black
black qgis_hub_plugin/

# Sort imports
isort qgis_hub_plugin/

# Lint code
flake8 qgis_hub_plugin/

# Run all pre-commit hooks on all files
pre-commit run --all-files
```

### Testing

```bash
# Run unit tests (fast, no QGIS needed)
pytest tests/unit/ -v

# Run with coverage report
pytest tests/unit/ --cov=qgis_hub_plugin --cov-report=html --cov-report=term

# Run specific test file
pytest tests/qgis/test_api_client_mocked.py -v

# Run QGIS integration tests (requires QGIS environment)
pytest tests/qgis/ -v

# Run all tests
pytest tests/ -v
```

### Git Workflow

Pre-commit hooks are automatically installed and will run on every commit:

```bash
# Make changes to code
# ...

# Stage your changes
git add .

# Commit (pre-commit hooks run automatically)
git commit -m "Your commit message"

# If hooks fail, fix the issues and commit again
```

The hooks will automatically:
- Check for large files
- Validate YAML/XML files
- Detect private keys
- Fix trailing whitespace
- Format code with black
- Sort imports with isort
- Run flake8 linting (on critical errors only)

## Virtual Environment Details

The virtual environment is configured with `--system-site-packages` to access PyQGIS and other system-installed QGIS libraries. This is required for QGIS plugin development.

### Environment Location
```
.venv/                # Virtual environment directory
├── bin/              # Executables (python, pip, pytest, etc.)
├── lib/              # Installed packages
└── pyvenv.cfg        # Configuration (includes system packages)
```

### Deactivating

To exit the virtual environment:

```bash
deactivate
```

### Re-activating

To return to development:

```bash
source .venv/bin/activate
```

## Troubleshooting

### Issue: `pytest` not found

**Solution:** Make sure the virtual environment is activated:
```bash
source .venv/bin/activate
```

### Issue: Pre-commit hooks not running

**Solution:** Re-install the hooks:
```bash
pre-commit install
```

### Issue: Import errors for PyQGIS

**Solution:** Ensure QGIS is installed on your system and the virtual environment was created with `--system-site-packages`:
```bash
python -c "from qgis.core import QgsApplication; print('PyQGIS OK')"
```

### Issue: Dependencies out of date

**Solution:** Update dependencies:
```bash
pip install -U -r requirements/development.txt
pip install -U -r requirements/testing.txt
```

## Adding New Dependencies

### Development Dependencies

Add to `requirements/development.txt`:
```bash
echo "new-package>=1.0" >> requirements/development.txt
pip install -r requirements/development.txt
```

### Testing Dependencies

Add to `requirements/testing.txt`:
```bash
echo "new-test-package>=1.0" >> requirements/testing.txt
pip install -r requirements/testing.txt
```

## CI/CD Integration

This development environment matches the CI/CD pipeline configuration:

- **Linter Workflow** (`.github/workflows/linter.yml`) - Runs flake8
- **Tester Workflow** (`.github/workflows/tester.yml`) - Runs pytest on unit tests
- **Pre-commit** - Same checks run locally and in CI

## Editor Integration

### VS Code

Recommended settings (`.vscode/settings.json`):

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "editor.formatOnSave": true
}
```

### PyCharm

1. File → Settings → Project → Python Interpreter
2. Click gear icon → Add
3. Select "Existing environment"
4. Browse to `.venv/bin/python`
5. Enable pytest as test runner in Settings → Tools → Python Integrated Tools

## Environment Summary

```
Python Version:     3.12.3
Virtual Environment: .venv/
System Packages:    Included (for PyQGIS)
Package Manager:    pip 25.2
Pre-commit:         Installed and active
Git Hooks:          Configured

Development Tools:
  - black 25.9.0
  - isort 5.13.2
  - flake8 7.3.0 (+ plugins)
  - pre-commit 3.8.0

Testing Tools:
  - pytest 8.4.2
  - pytest-cov 4.1.0
  - pytest-mock 3.15.1
```

## Next Steps

1. **Read the docs:** Check `docs/development/environment.md` for additional setup info
2. **Review architecture:** See `CLAUDE.md` for codebase architecture
3. **Run tests:** Execute `pytest tests/unit/ -v` to verify setup
4. **Start coding:** Follow the contribution guidelines in `CONTRIBUTING.md`

## Quick Reference Card

```bash
# Activate environment
source .venv/bin/activate

# Run tests
pytest tests/unit/ -v

# Format code
black qgis_hub_plugin/

# Lint code
flake8 qgis_hub_plugin/

# Run pre-commit checks
pre-commit run --all-files

# Deactivate environment
deactivate
```

---

**Setup Status:** ✅ Complete
**Last Updated:** 2025-10-24
**Environment Version:** 1.0
