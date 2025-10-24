# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QGIS Hub Plugin is a QGIS plugin that enables users to discover, browse, and integrate resources from the QGIS Hub service directly into their QGIS projects. Resources include processing models, styles, scripts, geopackages, layer definitions, 3D models, and more.

## Development Environment Setup

This plugin requires QGIS Python bindings (PyQGIS) which must be installed system-wide. The virtual environment must link to these system packages:

```bash
# Create virtual environment linking to system packages (for pyqgis)
python3 -m venv .venv --system-site-packages
source .venv/bin/activate

# Upgrade pip and install dependencies
python -m pip install -U pip setuptools wheel
python -m pip install -U -r requirements/development.txt

# Install pre-commit hooks
pre-commit install
```

## Common Development Commands

### Code Quality

```bash
# Run all pre-commit hooks on all files
pre-commit run --all-files

# Format code with black
black qgis_hub_plugin/

# Sort imports with isort
isort qgis_hub_plugin/

# Lint with flake8
flake8 qgis_hub_plugin/ --count --statistics
```

### Testing

```bash
# Run unit tests only (fast, no QGIS dependencies)
pytest tests/unit/ -v

# Run unit tests with coverage report
pytest tests/unit/ --cov=qgis_hub_plugin --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_api_client_mocked.py -v

# Run specific test
pytest tests/unit/test_api_client_mocked.py::TestApiClientMocked::test_get_all_resources_with_cache -v

# Run QGIS-specific tests (requires QGIS environment)
pytest tests/qgis/ -v

# Run all tests
pytest tests/ -v
```

**Test Structure:**
- `tests/unit/` - Unit tests without QGIS dependencies (use mocks)
  - `test_api_client_mocked.py` - API client with mocked network calls
  - `test_resource_item.py` - ResourceItem creation and data roles
  - `test_utilities.py` - Download functions and utilities
  - `test_plg_metadata.py` - Metadata parsing
- `tests/qgis/` - Integration tests requiring QGIS
  - `test_filter_proxy.py` - MultiRoleFilterProxyModel filtering/sorting
  - `test_integration.py` - End-to-end workflows
  - `test_api_client.py` - API client (original, makes real calls)
  - `test_plg_preferences.py` - Settings structure
- `tests/fixtures/` - Mock data for testing
  - `api_responses/` - Mock API response JSON files
- `tests/conftest.py` - Shared pytest fixtures

### Development Workflow

When making changes:
1. Make your code changes
2. Run `pre-commit run --all-files` to check code style
3. Run `pytest tests/unit/` to verify tests pass
4. Commit changes (pre-commit hooks will run automatically)

## Architecture Overview

### Plugin Entry Point and Lifecycle

- **Entry**: `qgis_hub_plugin/__init__.py` defines `classFactory(iface)` which QGIS calls to instantiate the plugin
- **Main Class**: `qgis_hub_plugin/plugin_main.py` contains `QgisHubPluginPlugin` class
  - `__init__(iface)`: Initialize plugin with QGIS interface
  - `initGui()`: Register UI elements (toolbar, menu items, settings widget)
  - `unload()`: Clean up on plugin disable

### Core Components

#### 1. API Client (`core/api_client.py`)
- **Function**: `get_all_resources(force_update=False)`
- Fetches resources from `https://hub.qgis.org/api/v1/resources/`
- Implements caching in `~/.qgis2/qgis_hub/response.json`
- Uses QGIS network utilities for HTTP requests

#### 2. GUI Components (`gui/`)

**Resource Browser** (`resource_browser.py`):
- Main dialog for browsing and managing resources (1,129 lines)
- Dual-view interface: Icon view and List view
- Tree-based category filtering with subtypes
- Full-text search across resource metadata
- Type-specific operations for downloading/adding resources to QGIS

**Resource Item** (`resource_item.py`):
- `ResourceItem(QStandardItem)`: Represents a single resource with metadata
- Custom Qt data roles for filtering (ResourceTypeRole, NameRole, CreatorRole, etc.)

**Settings Dialog** (`dlg_settings.py`):
- `ConfigOptionsPage`: Settings form integrated into QGIS Options menu
- `PlgOptionsFactory`: Factory for creating settings widgets

**Constants** (`constants.py`):
- Resource type definitions and categories
- Dynamic type registration for unknown resource types

#### 3. Filtering System (`core/custom_filter_proxy.py`)
- `MultiRoleFilterProxyModel(QSortFilterProxyModel)`: Advanced filtering
- Multi-role filtering (type, subtype, text search)
- Checkbox state management
- Custom sorting by integer values (download counts, dates)

#### 4. Utilities and Toolbelt

**Toolbelt** (`toolbelt/`):
- `log_handler.py`: `PlgLogger` - Logging with QGIS message bar integration
- `preferences.py`: `PlgOptionsManager` - Settings management with dataclass structure

**Utilities** (`utilities/`):
- `common.py`: File download, icon loading, thumbnail caching
- `exception.py`: Custom exceptions (DownloadError)
- `qgis_util.py`: `@show_busy_cursor` decorator for UI responsiveness
- `i18n.py`: Internationalization helpers

### QGIS Integration Points

1. **Menu Integration**: Adds "QGIS Hub Plugin" submenu to Plugins menu
2. **Toolbar**: Creates custom toolbar with Resource Browser action
3. **Settings**: Integrates into QGIS → Preferences → Options via `PlgOptionsFactory`
4. **Core APIs Used**:
   - `QgsApplication`: Network access, settings directory, processing registry
   - `QgsProject`: Layer operations
   - `QgsStyle`: Style database import
   - `QgsLayerDefinition`: Loading .qlr files
   - `QgsNetworkAccessManager`: HTTP requests

### Key Architectural Patterns

1. **Model-View-Proxy Pattern**:
   - Model: `QStandardItemModel` holds resource data
   - View: `ListView` (icon view) and `TreeView` (list view)
   - Proxy: `MultiRoleFilterProxyModel` for filtering without modifying source

2. **Separation of Concerns**:
   - API layer: Isolated in `api_client.py`
   - GUI layer: All UI components in `gui/` package
   - Core logic: Filtering in `core/` package
   - Utilities: Common operations in `utilities/` and `toolbelt/`

3. **Settings Management**:
   - Type-safe with dataclass (`PlgSettingsStructure`)
   - Centralized access via `PlgOptionsManager`
   - Stored in QgsSettings (QGIS configuration)

4. **Caching Strategy**:
   - API response cached to disk
   - Thumbnail caching in `~/.qgis2/qgis_hub/thumbnails/`
   - Smart refresh with `force_update` flag

5. **Dynamic Type Registration**:
   - Automatically handles new resource types from API
   - No code changes needed when QGIS Hub adds new types

6. **Error Handling**:
   - Custom exception hierarchy
   - User feedback via QGIS message bar
   - Logging at multiple levels

### Data Flow

```
User Opens Resource Browser
    ↓
get_all_resources() fetches from API (with caching)
    ↓
ResourceItem objects created for each resource
    ↓
QStandardItemModel populated
    ↓
MultiRoleFilterProxyModel applies filtering
    ↓
Display in ListView/TreeView
    ↓
User selects and downloads/adds resource
    ↓
Type-specific handler processes resource
    ↓
Resource integrated into QGIS
```

## Code Quality Standards

### Pre-commit Hooks

The project uses pre-commit hooks (`.pre-commit-config.yaml`) to enforce:
- Large file detection (max 500KB)
- XML/YAML validation
- Private key detection
- End-of-file fixer
- Trailing whitespace removal
- Python code upgrade to 3.9+ syntax

### Code Style

- **Formatting**: Black (no configuration needed)
- **Import Sorting**: isort with Black profile
- **Linting**: Flake8 with QGIS-specific rules
- **Docstrings**: Sphinx-style for technical documentation
- **Max Line Length**: 100 characters (flake8), 88 (black)
- **Max Complexity**: 15 (flake8)

### Flake8 Configuration

See `setup.cfg` for detailed flake8 rules. Key settings:
- Excludes: `.git`, `__pycache__`, `docs/conf.py`, `build`, `dist`, `.venv*`, `tests`
- Ignored rules: E121, E123, E126, E203, E226, E24, E704, QGS105, W503, W504
- QGIS-specific checks via `flake8-qgis` plugin

## Plugin Metadata

- **Name**: QGIS Hub Plugin
- **Category**: Web
- **Min QGIS Version**: 3.28
- **Authors**: Ismail Sunni, Ronit Jadhav
- **Homepage**: https://qgis.github.io/QGIS-Hub-Plugin/
- **Repository**: https://github.com/qgis/QGIS-Hub-Plugin
- **Tracker**: https://github.com/qgis/QGIS-Hub-Plugin/issues

## File Structure Reference

```
qgis_hub_plugin/
├── __init__.py                 # QGIS plugin entry point
├── plugin_main.py              # Main plugin class
├── __about__.py                # Metadata and version
├── metadata.txt                # QGIS plugin metadata
├── core/
│   ├── api_client.py           # API communication & caching
│   └── custom_filter_proxy.py # Advanced filtering logic
├── gui/
│   ├── resource_browser.py     # Main dialog (1,129 lines)
│   ├── resource_item.py        # Item models
│   ├── dlg_settings.py         # Settings page
│   └── constants.py            # Resource types & categories
├── toolbelt/
│   ├── log_handler.py          # Logging system
│   └── preferences.py          # Settings management
└── utilities/
    ├── common.py               # File operations, thumbnails
    ├── exception.py            # Custom exceptions
    ├── qgis_util.py            # QGIS utilities
    └── i18n.py                 # Internationalization
```

## CI/CD

The project uses GitHub Actions for:
- **Linter** (`.github/workflows/linter.yml`): Runs flake8 on Python code
- **Tester** (`.github/workflows/tester.yml`): Runs pytest on unit tests
- **Documentation** (`.github/workflows/documentation.yml`): Builds and publishes Sphinx docs
- **Releaser** (`.github/workflows/releaser.yml`): Packages and releases plugin

Tests run on push/PR when `**.py` files are modified.
