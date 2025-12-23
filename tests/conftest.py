#! python3  # noqa E265

"""
Shared pytest fixtures for QGIS Hub Plugin tests.

This module provides reusable fixtures for both unit and integration tests,
including mock API responses and sample resource data.
"""

import json
from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir():
    """Return path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_api_full_response(fixtures_dir):
    """Load full mock API response from fixtures.

    Returns:
        dict: Complete API response with 6 sample resources
    """
    fixture_path = fixtures_dir / "api_responses" / "full_response.json"
    with open(fixture_path) as f:
        return json.load(f)


@pytest.fixture
def mock_api_empty_response(fixtures_dir):
    """Load empty mock API response from fixtures.

    Returns:
        dict: API response with no results
    """
    fixture_path = fixtures_dir / "api_responses" / "empty_response.json"
    with open(fixture_path) as f:
        return json.load(f)


@pytest.fixture
def mock_api_paginated_response(fixtures_dir):
    """Load paginated mock API response from fixtures.

    Returns:
        dict: API response with pagination (next page)
    """
    fixture_path = fixtures_dir / "api_responses" / "paginated_response.json"
    with open(fixture_path) as f:
        return json.load(f)


@pytest.fixture
def sample_resource_dict(fixtures_dir):
    """Load single resource dictionary from fixtures.

    Returns:
        dict: Single resource with all fields including long name and dependencies
    """
    fixture_path = fixtures_dir / "api_responses" / "single_resource.json"
    with open(fixture_path) as f:
        return json.load(f)


@pytest.fixture
def sample_model_resource():
    """Provide a sample processing model resource.

    Returns:
        dict: Processing model resource dictionary
    """
    return {
        "uuid": "test-model-uuid",
        "name": "Test Processing Model",
        "resource_type": "model",
        "resource_subtype": "",
        "creator": "Test Creator",
        "upload_date": "2024-01-15T10:30:00Z",
        "download_count": 42,
        "description": "Test model description",
        "dependencies": [],
        "file": "https://example.com/model.model3",
        "thumbnail": "https://example.com/thumb.jpg",
    }


@pytest.fixture
def sample_style_resource():
    """Provide a sample style resource with subtype.

    Returns:
        dict: Style resource dictionary with symbol subtype
    """
    return {
        "uuid": "test-style-uuid",
        "name": "Test Symbol Style",
        "resource_type": "style",
        "resource_subtype": "symbol",
        "creator": "Style Author",
        "upload_date": "2024-02-10T14:20:00Z",
        "download_count": 128,
        "description": "Test style description",
        "dependencies": [],
        "file": "https://example.com/style.xml",
        "thumbnail": "https://example.com/style-thumb.jpg",
    }


@pytest.fixture
def sample_script_resource():
    """Provide a sample processing script with dependencies.

    Returns:
        dict: Processing script resource dictionary with dependencies
    """
    return {
        "uuid": "test-script-uuid",
        "name": "Test Python Script",
        "resource_type": "processingscript",
        "resource_subtype": "python",
        "creator": "Script Developer",
        "upload_date": "2024-03-05T09:15:00Z",
        "download_count": 87,
        "description": "Test script description",
        "dependencies": ["numpy", "pandas"],
        "file": "https://example.com/script.py",
        "thumbnail": None,
    }


@pytest.fixture
def sample_resources_list():
    """Provide a list of diverse sample resources.

    Returns:
        list: List of resource dictionaries with different types
    """
    return [
        {
            "uuid": "uuid-1",
            "name": "Model Resource",
            "resource_type": "model",
            "resource_subtype": "",
            "creator": "Creator 1",
            "upload_date": "2024-01-01T00:00:00Z",
            "download_count": 10,
            "description": "Model",
            "dependencies": [],
            "file": "https://example.com/model.model3",
            "thumbnail": "https://example.com/thumb1.jpg",
        },
        {
            "uuid": "uuid-2",
            "name": "Style Resource",
            "resource_type": "style",
            "resource_subtype": "symbol",
            "creator": "Creator 2",
            "upload_date": "2024-01-02T00:00:00Z",
            "download_count": 20,
            "description": "Style",
            "dependencies": [],
            "file": "https://example.com/style.xml",
            "thumbnail": "https://example.com/thumb2.jpg",
        },
        {
            "uuid": "uuid-3",
            "name": "Script Resource",
            "resource_type": "processingscript",
            "resource_subtype": "python",
            "creator": "Creator 3",
            "upload_date": "2024-01-03T00:00:00Z",
            "download_count": 30,
            "description": "Script",
            "dependencies": [],
            "file": "https://example.com/script.py",
            "thumbnail": None,
        },
    ]
