# Development

## Environment setup

> **Note:** A pre-configured virtual environment is already set up in this repository. See [DEVELOPMENT_SETUP.md](../../DEVELOPMENT_SETUP.md) for quick start instructions.

### First-time Setup (Ubuntu)

If the virtual environment doesn't exist or you need to recreate it:

```bash
# create virtual environment linking to system packages (for pyqgis)
python3 -m venv .venv --system-site-packages
source .venv/bin/activate

# bump dependencies inside venv
python -m pip install -U pip setuptools wheel
python -m pip install -U -r requirements/development.txt
python -m pip install -U -r requirements/testing.txt

# install git hooks (pre-commit)
pre-commit install
```

### Quick Start (Existing Setup)

If the virtual environment already exists:

```bash
# activate virtual environment
source .venv/bin/activate

# verify installation
python --version
pytest --version
```

## Installed Tools

The development environment includes:

- **black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting (with QGIS plugin)
- **pytest** - Testing framework
- **pre-commit** - Git hooks

## Common Tasks

```bash
# Run tests
pytest tests/unit/ -v

# Format code
black qgis_hub_plugin/

# Lint code
flake8 qgis_hub_plugin/

# Run pre-commit hooks
pre-commit run --all-files
```

For complete documentation, see [DEVELOPMENT_SETUP.md](../../DEVELOPMENT_SETUP.md).
