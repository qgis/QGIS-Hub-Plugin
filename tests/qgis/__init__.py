"""
QGIS integration tests.

These tests require a full QGIS environment and take longer to run.
They test the integration with QGIS GUI components and PyQGIS APIs.

To run only unit tests (skip QGIS tests):
    pytest tests/unit/ -v

To run all tests including QGIS:
    pytest tests/ -v

To explicitly skip QGIS tests:
    pytest tests/ -v -m "not qgis"
"""

import pytest

# Mark all tests in this directory as requiring QGIS
pytest_plugins = []
pytestmark = pytest.mark.qgis
