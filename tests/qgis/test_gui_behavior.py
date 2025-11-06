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


class TestResourceTreeFiltering(unittest.TestCase):
    """Tests for resource tree filtering functionality."""

    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_tree_setup_with_resources(self, mock_thumbnail, mock_api):
        """Test that resource tree is populated correctly with multiple resource types."""
        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock API response with diverse resource types
        mock_api.return_value = {
            "total": 4,
            "count": 4,
            "next": None,
            "results": [
                {
                    "uuid": "tree-model-1",
                    "name": "Test Model 1",
                    "resource_type": "model",
                    "resource_subtype": "",
                    "creator": "Test User",
                    "upload_date": "2024-01-15T10:30:00Z",
                    "download_count": 10,
                    "file": "https://example.com/model.model3",
                    "thumbnail": None,
                    "description": "Test model",
                    "dependencies": [],
                },
                {
                    "uuid": "tree-model-2",
                    "name": "Test Model 2",
                    "resource_type": "model",
                    "resource_subtype": "",
                    "creator": "Test User",
                    "upload_date": "2024-01-15T10:30:00Z",
                    "download_count": 15,
                    "file": "https://example.com/model2.model3",
                    "thumbnail": None,
                    "description": "Test model 2",
                    "dependencies": [],
                },
                {
                    "uuid": "tree-style-1",
                    "name": "Test Style",
                    "resource_type": "style",
                    "resource_subtype": "symbol",
                    "creator": "Test User",
                    "upload_date": "2024-01-15T10:30:00Z",
                    "download_count": 20,
                    "file": "https://example.com/style.xml",
                    "thumbnail": None,
                    "description": "Test style",
                    "dependencies": [],
                },
                {
                    "uuid": "tree-script-1",
                    "name": "Test Script",
                    "resource_type": "processingscript",
                    "resource_subtype": "python",
                    "creator": "Test User",
                    "upload_date": "2024-01-15T10:30:00Z",
                    "download_count": 25,
                    "file": "https://example.com/script.py",
                    "thumbnail": None,
                    "description": "Test script",
                    "dependencies": [],
                },
            ],
        }
        mock_thumbnail.return_value = None

        # Create dialog
        dialog = ResourceBrowserDialog()

        # Verify tree has items
        tree = dialog.treeWidgetCategories
        self.assertGreater(tree.topLevelItemCount(), 0)

        # Verify "All Types" is the top level item
        all_types_item = tree.topLevelItem(0)
        self.assertIsNotNone(all_types_item)
        self.assertIn("All Types", all_types_item.text(0))
        self.assertIn("4", all_types_item.text(0))  # Should show count

    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_tree_filtering_by_category(self, mock_thumbnail, mock_api):
        """Test that selecting a category in the tree filters resources correctly."""
        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock API response with multiple types
        mock_api.return_value = {
            "total": 3,
            "count": 3,
            "next": None,
            "results": [
                {
                    "uuid": "filter-model-1",
                    "name": "Model Resource",
                    "resource_type": "model",
                    "resource_subtype": "",
                    "creator": "Test User",
                    "upload_date": "2024-01-15T10:30:00Z",
                    "download_count": 10,
                    "file": "https://example.com/model.model3",
                    "thumbnail": None,
                    "description": "Test model",
                    "dependencies": [],
                },
                {
                    "uuid": "filter-style-1",
                    "name": "Style Resource",
                    "resource_type": "style",
                    "resource_subtype": "symbol",
                    "creator": "Test User",
                    "upload_date": "2024-01-15T10:30:00Z",
                    "download_count": 20,
                    "file": "https://example.com/style.xml",
                    "thumbnail": None,
                    "description": "Test style",
                    "dependencies": [],
                },
                {
                    "uuid": "filter-geopackage-1",
                    "name": "Geopackage Resource",
                    "resource_type": "geopackage",
                    "resource_subtype": "",
                    "creator": "Test User",
                    "upload_date": "2024-01-15T10:30:00Z",
                    "download_count": 30,
                    "file": "https://example.com/data.gpkg",
                    "thumbnail": None,
                    "description": "Test geopackage",
                    "dependencies": [],
                },
            ],
        }
        mock_thumbnail.return_value = None

        # Create dialog
        dialog = ResourceBrowserDialog()

        # Initially, all resources should be visible (3 resources)
        initial_count = dialog.proxy_model.rowCount()
        self.assertEqual(initial_count, 3)

        # Find and select a category item (e.g., "Models")
        tree = dialog.treeWidgetCategories
        all_types_item = tree.topLevelItem(0)

        # Find the Models category
        models_category = None
        for i in range(all_types_item.childCount()):
            child = all_types_item.child(i)
            if "Model" in child.text(0):
                models_category = child
                break

        if models_category:
            # Select the Models category
            tree.setCurrentItem(models_category)
            dialog.on_tree_selection_changed()

            # After filtering, only model resources should be visible
            filtered_count = dialog.proxy_model.rowCount()
            self.assertEqual(filtered_count, 1)  # Only 1 model in our test data

    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_tree_filtering_all_types(self, mock_thumbnail, mock_api):
        """Test that selecting 'All Types' shows all resources."""
        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock API response
        mock_api.return_value = {
            "total": 2,
            "count": 2,
            "next": None,
            "results": [
                {
                    "uuid": "all-model-1",
                    "name": "Model",
                    "resource_type": "model",
                    "resource_subtype": "",
                    "creator": "Test User",
                    "upload_date": "2024-01-15T10:30:00Z",
                    "download_count": 10,
                    "file": "https://example.com/model.model3",
                    "thumbnail": None,
                    "description": "Test model",
                    "dependencies": [],
                },
                {
                    "uuid": "all-style-1",
                    "name": "Style",
                    "resource_type": "style",
                    "resource_subtype": "symbol",
                    "creator": "Test User",
                    "upload_date": "2024-01-15T10:30:00Z",
                    "download_count": 20,
                    "file": "https://example.com/style.xml",
                    "thumbnail": None,
                    "description": "Test style",
                    "dependencies": [],
                },
            ],
        }
        mock_thumbnail.return_value = None

        # Create dialog
        dialog = ResourceBrowserDialog()

        # Select "All Types"
        tree = dialog.treeWidgetCategories
        all_types_item = tree.topLevelItem(0)
        tree.setCurrentItem(all_types_item)
        dialog.on_tree_selection_changed()

        # All resources should be visible
        total_count = dialog.proxy_model.rowCount()
        self.assertEqual(total_count, 2)


class TestPreviewFunctionality(unittest.TestCase):
    """Tests for resource preview functionality."""

    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_preview_updates_on_selection(self, mock_thumbnail, mock_api):
        """Test that preview panel updates when a resource is selected."""
        from pathlib import Path

        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock API response
        mock_api.return_value = {
            "total": 1,
            "count": 1,
            "next": None,
            "results": [
                {
                    "uuid": "preview-test-1",
                    "name": "Preview Test Resource",
                    "resource_type": "model",
                    "resource_subtype": "",
                    "creator": "Preview Creator",
                    "upload_date": "2024-03-15T14:30:00Z",
                    "download_count": 42,
                    "file": "https://example.com/preview.model3",
                    "thumbnail": None,
                    "description": "This is a test description for preview",
                    "dependencies": [],
                }
            ],
        }

        # Mock thumbnail to return a default path
        mock_thumbnail.return_value = Path("/tmp/default_icon.png")

        # Create dialog
        dialog = ResourceBrowserDialog()

        # Select the resource
        dialog.selected_resource = dialog.resource_model.item(0, 0)
        dialog.update_preview()

        # Verify preview labels are updated
        self.assertEqual(dialog.labelName.text(), "Preview Test Resource")
        self.assertEqual(dialog.labelCreator.text(), "Preview Creator")
        self.assertEqual(dialog.labelDownloadCount.text(), "42")

        # Verify description is set
        description_html = dialog.textBrowserDescription.toPlainText()
        self.assertIn("test description", description_html)

    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_preview_with_subtype(self, mock_thumbnail, mock_api):
        """Test that preview shows subtype information when available."""
        from pathlib import Path

        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock API response with subtype
        mock_api.return_value = {
            "total": 1,
            "count": 1,
            "next": None,
            "results": [
                {
                    "uuid": "subtype-test-1",
                    "name": "Style with Subtype",
                    "resource_type": "style",
                    "resource_subtype": "colorramp",
                    "creator": "Style Creator",
                    "upload_date": "2024-03-15T14:30:00Z",
                    "download_count": 15,
                    "file": "https://example.com/style.xml",
                    "thumbnail": None,
                    "description": "Color ramp style",
                    "dependencies": [],
                }
            ],
        }
        mock_thumbnail.return_value = Path("/tmp/default_icon.png")

        # Create dialog
        dialog = ResourceBrowserDialog()

        # Select the resource
        dialog.selected_resource = dialog.resource_model.item(0, 0)
        dialog.update_preview()

        # Verify subtype label is updated
        self.assertEqual(dialog.labelSubtype.text(), "colorramp")


class TestDownloadFunctionality(unittest.TestCase):
    """Tests for resource download functionality."""

    @patch("qgis_hub_plugin.gui.resource_browser.download_file")
    @patch("qgis_hub_plugin.gui.resource_browser.QFileDialog.getSaveFileName")
    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_download_resource_opens_file_dialog(
        self, mock_thumbnail, mock_api, mock_get_save_filename, mock_download
    ):
        """Test that download_resource opens a file dialog and downloads file."""
        from pathlib import Path

        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock API response
        mock_api.return_value = {
            "total": 1,
            "count": 1,
            "next": None,
            "results": [
                {
                    "uuid": "download-test-1",
                    "name": "Downloadable Resource",
                    "resource_type": "model",
                    "resource_subtype": "",
                    "creator": "Test Creator",
                    "upload_date": "2024-03-15T14:30:00Z",
                    "download_count": 10,
                    "file": "https://example.com/resource.model3",
                    "thumbnail": None,
                    "description": "Test resource for download",
                    "dependencies": [],
                }
            ],
        }
        mock_thumbnail.return_value = None

        # Mock file dialog to return a path without showing the dialog
        mock_get_save_filename.return_value = (
            "/tmp/downloaded_resource.model3",
            "Model files (*.model3)",
        )

        # Create dialog
        dialog = ResourceBrowserDialog()

        # Select the resource
        dialog.selected_resource = dialog.resource_model.item(0, 0)

        # Trigger download
        dialog.download_resource()

        # Verify file dialog was opened
        mock_get_save_filename.assert_called_once()

        # Verify download_file was called with correct arguments
        mock_download.assert_called_once()
        call_args = mock_download.call_args
        self.assertEqual(call_args[0][0], "https://example.com/resource.model3")
        self.assertEqual(call_args[0][1], Path("/tmp/downloaded_resource.model3"))

    @patch("qgis_hub_plugin.gui.resource_browser.QFileDialog.getSaveFileName")
    @patch("qgis_hub_plugin.gui.resource_browser.get_all_resources")
    @patch("qgis_hub_plugin.gui.resource_browser.download_resource_thumbnail")
    def test_download_cancelled_by_user(
        self, mock_thumbnail, mock_api, mock_get_save_filename
    ):
        """Test that download is cancelled when user closes file dialog without selecting."""
        from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog

        # Mock API response
        mock_api.return_value = {
            "total": 1,
            "count": 1,
            "next": None,
            "results": [
                {
                    "uuid": "cancel-test-1",
                    "name": "Test Resource",
                    "resource_type": "model",
                    "resource_subtype": "",
                    "creator": "Test Creator",
                    "upload_date": "2024-03-15T14:30:00Z",
                    "download_count": 10,
                    "file": "https://example.com/resource.model3",
                    "thumbnail": None,
                    "description": "Test resource",
                    "dependencies": [],
                }
            ],
        }
        mock_thumbnail.return_value = None

        # Mock file dialog to return empty (user cancelled) without showing dialog
        mock_get_save_filename.return_value = ("", "")

        # Create dialog
        dialog = ResourceBrowserDialog()

        # Select the resource
        dialog.selected_resource = dialog.resource_model.item(0, 0)

        # Trigger download
        dialog.download_resource()

        # Verify file dialog was opened
        mock_get_save_filename.assert_called_once()


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
