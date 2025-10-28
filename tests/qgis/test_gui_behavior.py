#! python3  # noqa E265

"""
Unit tests for QGIS Hub Plugin GUI behavior.

This test module verifies GUI interactions including view switching,
thumbnail size changes, and 'Add to QGIS' button behavior.

Usage from the repo root folder:

    .. code-block:: bash
        # for whole test module
        pytest tests/qgis/test_gui_behavior.py -v
        # for specific test
        pytest tests/qgis/test_gui_behavior.py::TestGUIBehavior::test_view_switching_icon_to_list -v
"""

import unittest
from unittest.mock import MagicMock, patch

from qgis.PyQt.QtCore import QSize
from qgis.testing import start_app

# Initialize QGIS application
start_app()


class TestGUIBehavior(unittest.TestCase):
    """Tests for GUI behavior and interactions."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Store original state if needed
        pass

    def tearDown(self):
        """Clean up after each test method."""
        pass

    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_view_switching_icon_to_list(self, mock_thumbnail, mock_api):
        """Test switching from icon view to list view."""
        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock API response with sample data
        mock_api.return_value = {
            "total": 1,
            "count": 1,
            "next": None,
            "results": [
                {
                    "uuid": "test-uuid-1",
                    "name": "Test Resource",
                    "resource_type": "model",
                    "resource_subtype": "",
                    "creator": "Test User",
                    "upload_date": "2024-01-15T10:30:00Z",
                    "download_count": 10,
                    "file": "https://example.com/model.model3",
                    "thumbnail": None,
                    "description": "Test model",
                    "dependencies": [],
                }
            ],
        }
        mock_thumbnail.return_value = None

        # Create dialog (starts in icon view by default)
        dialog = ResourceBrowserDialog()

        # Verify initial state - should be in icon view (index 0)
        self.assertEqual(dialog.viewStackedWidget.currentIndex(), 0)
        self.assertTrue(dialog.iconViewToolButton.isChecked())
        self.assertFalse(dialog.listViewToolButton.isChecked())

        # Switch to list view
        dialog.listViewToolButton.setChecked(True)
        dialog.show_list_view()

        # Verify switched to list view (index 1)
        self.assertEqual(dialog.viewStackedWidget.currentIndex(), 1)

    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_view_switching_list_to_icon(self, mock_thumbnail, mock_api):
        """Test switching from list view to icon view."""
        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock API response
        mock_api.return_value = {
            "total": 1,
            "count": 1,
            "next": None,
            "results": [
                {
                    "uuid": "test-uuid-2",
                    "name": "Test Resource 2",
                    "resource_type": "style",
                    "resource_subtype": "symbol",
                    "creator": "Test User",
                    "upload_date": "2024-01-15T10:30:00Z",
                    "download_count": 5,
                    "file": "https://example.com/style.xml",
                    "thumbnail": None,
                    "description": "Test style",
                    "dependencies": [],
                }
            ],
        }
        mock_thumbnail.return_value = None

        # Create dialog and switch to list view first
        dialog = ResourceBrowserDialog()
        dialog.listViewToolButton.setChecked(True)
        dialog.show_list_view()

        # Verify we're in list view
        self.assertEqual(dialog.viewStackedWidget.currentIndex(), 1)

        # Switch to icon view
        dialog.iconViewToolButton.setChecked(True)
        dialog.show_icon_view()

        # Verify switched to icon view (index 0)
        self.assertEqual(dialog.viewStackedWidget.currentIndex(), 0)

    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_thumbnail_size_change(self, mock_thumbnail, mock_api):
        """Test changing thumbnail size with slider."""
        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock API response
        mock_api.return_value = {
            "total": 1,
            "count": 1,
            "next": None,
            "results": [
                {
                    "uuid": "test-uuid-3",
                    "name": "Test Resource 3",
                    "resource_type": "model",
                    "resource_subtype": "",
                    "creator": "Test User",
                    "upload_date": "2024-01-15T10:30:00Z",
                    "download_count": 10,
                    "file": "https://example.com/model.model3",
                    "thumbnail": None,
                    "description": "Test model",
                    "dependencies": [],
                }
            ],
        }
        mock_thumbnail.return_value = None

        # Create dialog
        dialog = ResourceBrowserDialog()

        # Verify slider range
        self.assertEqual(dialog.iconSizeSlider.minimum(), 20)
        self.assertEqual(dialog.iconSizeSlider.maximum(), 128)

        # Test setting different sizes
        test_sizes = [20, 50, 74, 100, 128]
        for size in test_sizes:
            dialog.iconSizeSlider.setValue(size)
            dialog.update_icon_size(size)

            # Verify icon size was updated
            icon_size = dialog.listViewResources.iconSize()
            self.assertEqual(icon_size.width(), size)
            self.assertEqual(icon_size.height(), size)

    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_thumbnail_size_slider_signal(self, mock_thumbnail, mock_api):
        """Test that slider valueChanged signal updates icon size."""
        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock API response
        mock_api.return_value = {
            "total": 1,
            "count": 1,
            "next": None,
            "results": [
                {
                    "uuid": "test-uuid-4",
                    "name": "Test Resource 4",
                    "resource_type": "style",
                    "resource_subtype": "symbol",
                    "creator": "Test User",
                    "upload_date": "2024-01-15T10:30:00Z",
                    "download_count": 15,
                    "file": "https://example.com/style.xml",
                    "thumbnail": None,
                    "description": "Test style",
                    "dependencies": [],
                }
            ],
        }
        mock_thumbnail.return_value = None

        # Create dialog
        dialog = ResourceBrowserDialog()

        # Change slider value (this should trigger valueChanged signal)
        new_size = 80
        dialog.iconSizeSlider.setValue(new_size)

        # Verify icon size was updated via the signal connection
        icon_size = dialog.listViewResources.iconSize()
        self.assertEqual(icon_size.width(), new_size)
        self.assertEqual(icon_size.height(), new_size)


class TestViewPersistence(unittest.TestCase):
    """Tests for view state persistence across sessions."""

    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_view_state_persistence(self, mock_thumbnail, mock_api):
        """Test that view state is saved and restored correctly."""
        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock API response
        mock_api.return_value = {
            "total": 1,
            "count": 1,
            "next": None,
            "results": [
                {
                    "uuid": "test-persist-uuid",
                    "name": "Test Persist",
                    "resource_type": "model",
                    "resource_subtype": "",
                    "creator": "Test User",
                    "upload_date": "2024-01-15T10:30:00Z",
                    "download_count": 10,
                    "file": "https://example.com/model.model3",
                    "thumbnail": None,
                    "description": "Test model",
                    "dependencies": [],
                }
            ],
        }
        mock_thumbnail.return_value = None

        # Create dialog and switch to list view
        dialog = ResourceBrowserDialog()
        dialog.viewStackedWidget.setCurrentIndex(1)

        # Store settings
        dialog.store_setting()

        # Verify the setting was stored
        stored_view_index = dialog.plg_settings.get_value_from_key(
            "current_view_index", 0, int
        )
        self.assertEqual(stored_view_index, 1)

    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_icon_size_persistence(self, mock_thumbnail, mock_api):
        """Test that icon size is saved and restored correctly."""
        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock API response
        mock_api.return_value = {
            "total": 1,
            "count": 1,
            "next": None,
            "results": [
                {
                    "uuid": "test-size-persist-uuid",
                    "name": "Test Size Persist",
                    "resource_type": "style",
                    "resource_subtype": "symbol",
                    "creator": "Test User",
                    "upload_date": "2024-01-15T10:30:00Z",
                    "download_count": 15,
                    "file": "https://example.com/style.xml",
                    "thumbnail": None,
                    "description": "Test style",
                    "dependencies": [],
                }
            ],
        }
        mock_thumbnail.return_value = None

        # Create dialog and set icon size
        dialog = ResourceBrowserDialog()
        test_size = 96
        dialog.iconSizeSlider.setValue(test_size)

        # Store settings
        dialog.store_setting()

        # Verify the setting was stored
        stored_size = dialog.plg_settings.get_value_from_key("icon_size", 74, int)
        self.assertEqual(stored_size, test_size)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
