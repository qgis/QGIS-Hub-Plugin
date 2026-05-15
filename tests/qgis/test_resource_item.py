#! python3  # noqa E265

"""
Unit tests for ResourceItem and AttributeSortingItem classes.

This test module verifies resource item creation, data roles,
name truncation, and sorting functionality.

Usage from the repo root folder:

    .. code-block:: bash
        # for whole test module
        pytest tests/qgis/test_resource_item.py -v
        # for specific test
        pytest tests/qgis/test_resource_item.py::TestResourceItem::test_resource_item_creation -v
"""

import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# Try to import QIcon and ResourceItem from QGIS for use in mocks
try:
    from qgis.PyQt.QtGui import QIcon
    from qgis.testing import start_app

    from qgis_hub_plugin.gui.resource_item import ResourceItem

    # Ensure a QApplication exists for tests that build real QPixmap/QIcon
    start_app()
except ImportError:
    # Create mock classes for when QGIS is not available
    QIcon = MagicMock
    ResourceItem = MagicMock


class TestResourceItem(unittest.TestCase):
    """Test ResourceItem class."""

    def setUp(self):
        """Create sample resource data."""
        self.sample_resource = {
            "uuid": "test-uuid-123",
            "name": "Test Resource",
            "resource_type": "model",
            "resource_subtype": "",
            "creator": "Test Creator",
            "upload_date": "2024-01-15T10:30:00Z",
            "download_count": 42,
            "description": "Test description",
            "dependencies": [],
            "file": "https://example.com/file.model3",
            "thumbnail": "https://example.com/thumb.jpg",
        }

    @patch("qgis_hub_plugin.gui.resource_item.download_resource_thumbnail")
    @patch("qgis_hub_plugin.gui.resource_item.get_icon")
    def test_resource_item_creation(self, mock_get_icon, mock_download_thumb):
        """Test ResourceItem initialization with all fields."""
        from qgis_hub_plugin.gui.constants import (
            CreatorRole,
            NameRole,
            ResourceSubtypeRole,
            ResourceTypeRole,
        )
        from qgis_hub_plugin.gui.resource_item import ResourceItem

        # Mock thumbnail download returns None (use default icon)
        mock_download_thumb.return_value = None
        mock_icon = QIcon()
        mock_get_icon.return_value = mock_icon

        item = ResourceItem(self.sample_resource)

        # Verify basic attributes
        self.assertEqual(item.uuid, "test-uuid-123")
        self.assertEqual(item.name, "Test Resource")
        self.assertEqual(item.resource_type, "model")
        self.assertEqual(item.resource_subtype, "")
        self.assertEqual(item.creator, "Test Creator")
        self.assertEqual(item.download_count, 42)
        self.assertEqual(item.description, "Test description")
        self.assertEqual(item.dependencies, [])
        self.assertEqual(item.file, "https://example.com/file.model3")
        self.assertEqual(item.thumbnail, "https://example.com/thumb.jpg")

        # Verify upload_date parsed correctly
        self.assertIsInstance(item.upload_date, datetime)
        self.assertEqual(item.upload_date.year, 2024)
        self.assertEqual(item.upload_date.month, 1)
        self.assertEqual(item.upload_date.day, 15)

        # Verify text and tooltip
        self.assertEqual(item.text(), "Test Resource")
        self.assertEqual(item.toolTip(), "Test Resource by Test Creator")

        # Verify data roles
        self.assertEqual(item.data(ResourceTypeRole), "model")
        self.assertEqual(item.data(NameRole), "Test Resource")
        self.assertEqual(item.data(CreatorRole), "Test Creator")
        self.assertEqual(item.data(ResourceSubtypeRole), [])

        # Verify icon was set
        mock_download_thumb.assert_called_once_with(
            "https://example.com/thumb.jpg", "test-uuid-123"
        )
        mock_get_icon.assert_called_once_with("QGIS_Hub_icon.svg")

    @patch("qgis_hub_plugin.gui.resource_item.download_resource_thumbnail")
    @patch("qgis_hub_plugin.gui.resource_item.get_icon")
    def test_long_name_truncation(self, mock_get_icon, mock_download_thumb):
        """Test that long names are truncated to 50 chars + '...'"""
        from qgis_hub_plugin.gui.resource_item import ResourceItem

        mock_download_thumb.return_value = None
        mock_get_icon.return_value = QIcon()

        # Create resource with very long name (100 characters)
        long_name = "A" * 100
        self.sample_resource["name"] = long_name

        item = ResourceItem(self.sample_resource)

        # Verify name is truncated
        self.assertTrue(item.text().endswith("..."))
        self.assertEqual(len(item.text()), 53)  # 50 + "..."
        self.assertEqual(item.text(), "A" * 50 + "...")

        # But original name should be preserved in item.name
        self.assertEqual(item.name, long_name)

    @patch("qgis_hub_plugin.gui.resource_item.download_resource_thumbnail")
    @patch.object(ResourceItem, "_make_uniform_icon", return_value=QIcon())
    def test_thumbnail_icon_loading(self, mock_make_icon, mock_download_thumb):
        """Test that thumbnail is downloaded and passed to the icon builder."""
        from pathlib import Path

        from qgis_hub_plugin.gui.resource_item import ResourceItem

        mock_thumb_path = Path("/tmp/thumb.jpg")
        mock_download_thumb.return_value = mock_thumb_path

        item = ResourceItem(self.sample_resource)

        # Verify thumbnail was downloaded with correct arguments
        mock_download_thumb.assert_called_once_with(
            "https://example.com/thumb.jpg", "test-uuid-123"
        )
        # Verify the downloaded path was passed to the icon builder
        mock_make_icon.assert_called_once_with(mock_thumb_path)

    @patch("qgis_hub_plugin.gui.resource_item.download_resource_thumbnail")
    @patch("qgis_hub_plugin.gui.resource_item.get_icon")
    def test_resource_with_subtype(self, mock_get_icon, mock_download_thumb):
        """Test resource with subtype (e.g., style:symbol)."""
        from qgis_hub_plugin.gui.constants import ResourceSubtypeRole
        from qgis_hub_plugin.gui.resource_item import ResourceItem

        mock_download_thumb.return_value = None
        mock_get_icon.return_value = QIcon()

        self.sample_resource["resource_type"] = "style"
        self.sample_resource["resource_subtype"] = "symbol"

        item = ResourceItem(self.sample_resource)

        self.assertEqual(item.resource_type, "style")
        self.assertEqual(item.resource_subtype, "symbol")
        # Now subtypes are stored as list in the role
        self.assertEqual(item.resource_subtypes, ["symbol"])
        self.assertEqual(item.data(ResourceSubtypeRole), ["symbol"])

    @patch("qgis_hub_plugin.gui.resource_item.download_resource_thumbnail")
    @patch("qgis_hub_plugin.gui.resource_item.get_icon")
    def test_resource_with_dependencies(self, mock_get_icon, mock_download_thumb):
        """Test resource with dependencies list."""
        from qgis_hub_plugin.gui.resource_item import ResourceItem

        mock_download_thumb.return_value = None
        mock_get_icon.return_value = QIcon()

        self.sample_resource["dependencies"] = ["numpy", "pandas", "geopandas"]

        item = ResourceItem(self.sample_resource)

        self.assertEqual(len(item.dependencies), 3)
        self.assertIn("numpy", item.dependencies)
        self.assertIn("pandas", item.dependencies)

    @patch("qgis_hub_plugin.gui.resource_item.download_resource_thumbnail")
    @patch("qgis_hub_plugin.gui.resource_item.get_icon")
    def test_resource_with_whitespace_in_name(self, mock_get_icon, mock_download_thumb):
        """Test that whitespace is stripped from name and creator."""
        from qgis_hub_plugin.gui.resource_item import ResourceItem

        mock_download_thumb.return_value = None
        mock_get_icon.return_value = QIcon()

        self.sample_resource["name"] = "  Test Resource  "
        self.sample_resource["creator"] = "  Test Creator  "

        item = ResourceItem(self.sample_resource)

        # Verify whitespace is stripped
        self.assertEqual(item.name, "Test Resource")
        self.assertEqual(item.creator, "Test Creator")


class TestMakeUniformIcon(unittest.TestCase):
    """Test ResourceItem._make_uniform_icon."""

    def test_fallback_when_path_is_none(self):
        """None path returns the default hub icon."""
        from qgis_hub_plugin.gui.resource_item import ResourceItem

        icon = ResourceItem._make_uniform_icon(None)
        self.assertIsInstance(icon, QIcon)
        self.assertFalse(icon.isNull())

    def test_fallback_when_path_is_default_hub_icon(self):
        """A path pointing at the bundled QGIS_Hub_icon.svg short-circuits."""
        from pathlib import Path

        from qgis_hub_plugin.gui.resource_item import ResourceItem

        icon = ResourceItem._make_uniform_icon(Path("/x/QGIS_Hub_icon.svg"))
        self.assertIsInstance(icon, QIcon)
        self.assertFalse(icon.isNull())

    def test_fallback_when_pixmap_is_null(self):
        """Unreadable thumbnail file falls back to default icon."""
        import tempfile
        from pathlib import Path

        from qgis_hub_plugin.gui.resource_item import ResourceItem

        with tempfile.TemporaryDirectory() as tmpdir:
            bogus = Path(tmpdir) / "broken.jpg"
            bogus.write_bytes(b"not a real image")

            icon = ResourceItem._make_uniform_icon(bogus)
            self.assertIsInstance(icon, QIcon)
            self.assertFalse(icon.isNull())

    def test_returns_square_canvas_for_valid_image(self):
        """Valid thumbnail is centered on a square canvas of target_size."""
        import tempfile
        from pathlib import Path

        from qgis.PyQt.QtGui import QImage

        from qgis_hub_plugin.gui.resource_item import ResourceItem

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a non-square test image so we can verify the canvas is square
            src = Path(tmpdir) / "thumb.png"
            img = QImage(80, 40, QImage.Format.Format_ARGB32)
            img.fill(0xFF0000FF)
            self.assertTrue(img.save(str(src), "PNG"))

            icon = ResourceItem._make_uniform_icon(src, target_size=128)
            self.assertIsInstance(icon, QIcon)
            self.assertFalse(icon.isNull())

            pixmap = icon.pixmap(128, 128)
            self.assertEqual(pixmap.width(), 128)
            self.assertEqual(pixmap.height(), 128)


class TestAttributeSortingItem(unittest.TestCase):
    """Test AttributeSortingItem class."""

    def test_attribute_sorting_item_creation(self):
        """Test AttributeSortingItem with display and sortable value."""
        from qgis_hub_plugin.gui.constants import SortingRole
        from qgis_hub_plugin.gui.resource_item import AttributeSortingItem

        item = AttributeSortingItem("42 downloads", 42)

        # Verify display text
        self.assertEqual(item.text(), "42 downloads")

        # Verify sorting value
        self.assertEqual(item.data(SortingRole), 42)

    def test_attribute_sorting_item_date(self):
        """Test AttributeSortingItem with date values."""
        from datetime import datetime

        from qgis_hub_plugin.gui.constants import SortingRole
        from qgis_hub_plugin.gui.resource_item import AttributeSortingItem

        date_value = datetime(2024, 1, 15, 10, 30)
        timestamp = int(date_value.timestamp())

        item = AttributeSortingItem("2024-01-15", timestamp)

        self.assertEqual(item.text(), "2024-01-15")
        self.assertEqual(item.data(SortingRole), timestamp)


# ############################################################################
# ######### Pytest-style tests ###############
# ############################################


@pytest.mark.parametrize(
    "name,expected_text",
    [
        ("Short", "Short"),
        (
            "Exactly fifty characters in this name here test!!",
            "Exactly fifty characters in this name here test!!",
        ),
        ("A" * 50, "A" * 50),
        ("A" * 51, "A" * 50 + "..."),
        ("A" * 100, "A" * 50 + "..."),
    ],
)
def test_name_truncation_parameterized(name, expected_text, sample_model_resource):
    """Test various name lengths for truncation.

    Args:
        name: Resource name to test
        expected_text: Expected display text
        sample_model_resource: Fixture providing sample resource
    """
    from qgis_hub_plugin.gui.resource_item import ResourceItem

    with patch("qgis_hub_plugin.gui.resource_item.download_resource_thumbnail"):
        with patch("qgis_hub_plugin.gui.resource_item.get_icon", return_value=QIcon()):
            sample_model_resource["name"] = name
            item = ResourceItem(sample_model_resource)
            assert item.text() == expected_text


@pytest.mark.parametrize(
    "resource_type,subtype",
    [
        ("model", ""),
        ("style", "symbol"),
        ("style", "colorramp"),
        ("processingscript", "python"),
        ("processingscript", "r"),
        ("geopackage", ""),
        ("layerdefinition", ""),
    ],
)
def test_various_resource_types(resource_type, subtype, sample_model_resource):
    """Test ResourceItem with various types and subtypes.

    Args:
        resource_type: Type of resource
        subtype: Subtype of resource
        sample_model_resource: Fixture providing sample resource
    """
    from qgis_hub_plugin.gui.constants import ResourceSubtypeRole, ResourceTypeRole
    from qgis_hub_plugin.gui.resource_item import ResourceItem

    with patch("qgis_hub_plugin.gui.resource_item.download_resource_thumbnail"):
        with patch("qgis_hub_plugin.gui.resource_item.get_icon", return_value=QIcon()):
            sample_model_resource["resource_type"] = resource_type
            sample_model_resource["resource_subtype"] = subtype

            item = ResourceItem(sample_model_resource)

            assert item.resource_type == resource_type
            assert item.resource_subtype == subtype
            assert item.data(ResourceTypeRole) == resource_type
            # For backward compatibility, data should now be a list
            expected_subtypes = [subtype] if subtype else []
            assert item.data(ResourceSubtypeRole) == expected_subtypes


@pytest.mark.parametrize(
    "subtypes,expected_list,expected_first",
    [
        ([], [], ""),
        (["symbol"], ["symbol"], "symbol"),
        (["symbol", "colorramp"], ["symbol", "colorramp"], "symbol"),
        (["python", "r", "qgis"], ["python", "r", "qgis"], "python"),
    ],
)
def test_resource_with_multiple_subtypes(
    subtypes, expected_list, expected_first, sample_model_resource
):
    """Test ResourceItem with new resource_subtypes array format.

    Args:
        subtypes: Array of subtypes to test
        expected_list: Expected subtypes list
        expected_first: Expected first subtype (backward compatibility)
        sample_model_resource: Fixture providing sample resource
    """
    from qgis_hub_plugin.gui.constants import ResourceSubtypeRole
    from qgis_hub_plugin.gui.resource_item import ResourceItem

    with patch("qgis_hub_plugin.gui.resource_item.download_resource_thumbnail"):
        with patch("qgis_hub_plugin.gui.resource_item.get_icon", return_value=QIcon()):
            sample_model_resource["resource_type"] = "style"
            sample_model_resource["resource_subtypes"] = subtypes
            # Remove old field if present
            sample_model_resource.pop("resource_subtype", None)

            item = ResourceItem(sample_model_resource)

            assert item.resource_type == "style"
            assert item.resource_subtypes == expected_list
            # Backward compatibility - first subtype or empty string
            assert item.resource_subtype == expected_first
            # Data role should contain the list
            assert item.data(ResourceSubtypeRole) == expected_list


def test_backward_compatibility_old_api_format(sample_model_resource):
    """Test backward compatibility with old resource_subtype format.

    Args:
        sample_model_resource: Fixture providing sample resource
    """
    from qgis_hub_plugin.gui.constants import ResourceSubtypeRole
    from qgis_hub_plugin.gui.resource_item import ResourceItem

    with patch("qgis_hub_plugin.gui.resource_item.download_resource_thumbnail"):
        with patch("qgis_hub_plugin.gui.resource_item.get_icon", return_value=QIcon()):
            # Use old API format with resource_subtype
            sample_model_resource["resource_type"] = "style"
            sample_model_resource["resource_subtype"] = "symbol"
            # Ensure new field doesn't exist
            sample_model_resource.pop("resource_subtypes", None)

            item = ResourceItem(sample_model_resource)

            # Should convert to list internally
            assert item.resource_subtypes == ["symbol"]
            assert item.resource_subtype == "symbol"
            assert item.data(ResourceSubtypeRole) == ["symbol"]


def test_empty_subtype_backward_compatibility(sample_model_resource):
    """Test empty subtype with old API format.

    Args:
        sample_model_resource: Fixture providing sample resource
    """
    from qgis_hub_plugin.gui.constants import ResourceSubtypeRole
    from qgis_hub_plugin.gui.resource_item import ResourceItem

    with patch("qgis_hub_plugin.gui.resource_item.download_resource_thumbnail"):
        with patch("qgis_hub_plugin.gui.resource_item.get_icon", return_value=QIcon()):
            sample_model_resource["resource_subtype"] = ""
            sample_model_resource.pop("resource_subtypes", None)

            item = ResourceItem(sample_model_resource)

            assert item.resource_subtypes == []
            assert item.resource_subtype == ""
            assert item.data(ResourceSubtypeRole) == []


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
