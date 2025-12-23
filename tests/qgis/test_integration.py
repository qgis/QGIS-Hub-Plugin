#! python3  # noqa E265

"""
Integration tests for QGIS Hub Plugin.

This test module verifies end-to-end workflows including
API data loading, resource browser initialization, and filtering.

Usage from the repo root folder:

    .. code-block:: bash
        # for whole test module
        pytest tests/qgis/test_integration.py -v
        # for specific test
        pytest tests/qgis/test_integration.py::TestIntegration::test_full_resource_load_workflow -v
"""

import unittest
from unittest.mock import patch

from qgis.testing import start_app

# Initialize QGIS application
start_app()


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""

    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_full_resource_load_workflow(self, mock_thumbnail, mock_api):
        """Test complete workflow from API to GUI display."""
        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock API response
        mock_api.return_value = {
            "total": 3,
            "count": 3,
            "next": None,
            "results": [
                {
                    "uuid": "integration-uuid-1",
                    "name": "Integration Test Model",
                    "resource_type": "model",
                    "resource_subtype": "",
                    "creator": "Test User",
                    "upload_date": "2024-01-15T10:30:00Z",
                    "download_count": 10,
                    "file": "https://example.com/model.model3",
                    "thumbnail": None,
                    "description": "Integration test",
                    "dependencies": [],
                },
                {
                    "uuid": "integration-uuid-2",
                    "name": "Integration Test Style",
                    "resource_type": "style",
                    "resource_subtype": "symbol",
                    "creator": "Style Creator",
                    "upload_date": "2024-02-10T14:20:00Z",
                    "download_count": 25,
                    "file": "https://example.com/style.xml",
                    "thumbnail": None,
                    "description": "Test style",
                    "dependencies": [],
                },
                {
                    "uuid": "integration-uuid-3",
                    "name": "Integration Test Script",
                    "resource_type": "processingscript",
                    "resource_subtype": "python",
                    "creator": "Script Author",
                    "upload_date": "2024-03-05T09:15:00Z",
                    "download_count": 15,
                    "file": "https://example.com/script.py",
                    "thumbnail": None,
                    "description": "Test script",
                    "dependencies": ["numpy"],
                },
            ],
        }

        # Mock thumbnail download
        mock_thumbnail.return_value = None

        # Create dialog (this should trigger resource loading)
        dialog = ResourceBrowserDialog()

        # Verify API was called
        mock_api.assert_called()

        # Verify resources were loaded into model
        self.assertGreater(dialog.resource_model.rowCount(), 0)
        self.assertEqual(dialog.resource_model.rowCount(), 3)

        # Verify resource types are diverse
        resource_types = set()
        for row in range(dialog.resource_model.rowCount()):
            item = dialog.resource_model.item(row, 0)
            from qgis_hub_plugin.gui.constants import ResourceTypeRole

            resource_type = item.data(ResourceTypeRole)
            resource_types.add(resource_type)

        self.assertIn("model", resource_types)
        self.assertIn("style", resource_types)
        self.assertIn("processingscript", resource_types)

    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_resource_browser_with_empty_response(self, mock_thumbnail, mock_api):
        """Test resource browser handles empty API response."""
        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock empty API response
        mock_api.return_value = {"total": 0, "count": 0, "next": None, "results": []}

        mock_thumbnail.return_value = None

        # Create dialog
        dialog = ResourceBrowserDialog()

        # Verify model is empty
        self.assertEqual(dialog.resource_model.rowCount(), 0)

    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_resource_filtering_integration(self, mock_thumbnail, mock_api):
        """Test that filtering works with loaded resources."""
        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock API with multiple resource types
        mock_api.return_value = {
            "total": 4,
            "count": 4,
            "next": None,
            "results": [
                {
                    "uuid": f"filter-test-{i}",
                    "name": f"Resource {i}",
                    "resource_type": resource_type,
                    "resource_subtype": "",
                    "creator": "Test Creator",
                    "upload_date": "2024-01-01T00:00:00Z",
                    "download_count": i * 10,
                    "file": f"https://example.com/file{i}",
                    "thumbnail": None,
                    "description": f"Resource {i}",
                    "dependencies": [],
                }
                for i, resource_type in enumerate(
                    ["model", "model", "style", "processingscript"]
                )
            ],
        }

        mock_thumbnail.return_value = None

        # Create dialog
        dialog = ResourceBrowserDialog()

        # Verify all resources loaded
        self.assertEqual(dialog.resource_model.rowCount(), 4)

        # Apply filter to show only models
        from qgis_hub_plugin.gui.constants import NameRole

        dialog.proxy_model.setCheckboxStates({"model": True})
        dialog.proxy_model.setRolesToFilter([NameRole])

        # Verify only 2 models are shown
        self.assertEqual(dialog.proxy_model.rowCount(), 2)

    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    def test_resource_browser_handles_api_failure(self, mock_api):
        """Test that resource browser handles API failure gracefully."""
        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock API failure (returns None)
        mock_api.return_value = None

        # Create dialog - should not crash
        try:
            dialog = ResourceBrowserDialog()
            # If API returns None, model should be empty
            self.assertEqual(dialog.resource_model.rowCount(), 0)
        except Exception as e:
            self.fail(f"Dialog creation failed with API error: {e}")

    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_resource_with_dependencies(self, mock_thumbnail, mock_api):
        """Test that resources with dependencies are loaded correctly."""
        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock resource with dependencies
        mock_api.return_value = {
            "total": 1,
            "count": 1,
            "next": None,
            "results": [
                {
                    "uuid": "deps-test-uuid",
                    "name": "Script with Dependencies",
                    "resource_type": "processingscript",
                    "resource_subtype": "python",
                    "creator": "Developer",
                    "upload_date": "2024-01-01T00:00:00Z",
                    "download_count": 5,
                    "file": "https://example.com/script.py",
                    "thumbnail": None,
                    "description": "Script needing libraries",
                    "dependencies": ["numpy", "pandas", "geopandas"],
                }
            ],
        }

        mock_thumbnail.return_value = None

        # Create dialog
        dialog = ResourceBrowserDialog()

        # Verify resource loaded
        self.assertEqual(dialog.resource_model.rowCount(), 1)

        # Get the resource item
        item = dialog.resource_model.item(0, 0)

        # Verify dependencies
        self.assertIsNotNone(item.dependencies)
        self.assertEqual(len(item.dependencies), 3)
        self.assertIn("numpy", item.dependencies)


class TestResourceItemIntegration(unittest.TestCase):
    """Integration tests for ResourceItem in model context."""

    @patch("qgis_hub_plugin.gui.resource_item.download_resource_thumbnail")
    def test_multiple_resource_items_in_model(self, mock_thumbnail):
        """Test adding multiple ResourceItem objects to a model."""
        from qgis.PyQt.QtGui import QStandardItemModel

        from qgis_hub_plugin.gui.resource_item import ResourceItem

        mock_thumbnail.return_value = None

        model = QStandardItemModel()

        # Create multiple resources
        resources = [
            {
                "uuid": f"multi-test-{i}",
                "name": f"Resource {i}",
                "resource_type": "model" if i % 2 == 0 else "style",
                "resource_subtype": "",
                "creator": f"Creator {i}",
                "upload_date": "2024-01-01T00:00:00Z",
                "download_count": i * 10,
                "file": f"https://example.com/file{i}",
                "thumbnail": None,
                "description": f"Description {i}",
                "dependencies": [],
            }
            for i in range(10)
        ]

        # Add all to model
        for resource in resources:
            item = ResourceItem(resource)
            model.appendRow(item)

        # Verify all added
        self.assertEqual(model.rowCount(), 10)

        # Verify data integrity
        for row in range(model.rowCount()):
            item = model.item(row, 0)
            self.assertIsNotNone(item.uuid)
            self.assertIsNotNone(item.name)
            self.assertIsNotNone(item.resource_type)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
