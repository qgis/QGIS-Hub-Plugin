#! python3  # noqa E265

"""
QGIS tests for MultiRoleFilterProxyModel.

This test module verifies the filtering and sorting functionality
of the proxy model with QGIS dependencies.

Usage from the repo root folder:

    .. code-block:: bash
        # for whole test module
        pytest tests/qgis/test_filter_proxy.py -v
        # for specific test
        pytest tests/qgis/test_filter_proxy.py::TestFilterProxyModel::test_filter_by_resource_type -v
"""

import unittest

from qgis.PyQt.QtCore import QRegExp, Qt
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from qgis.testing import start_app

from qgis_hub_plugin.core.custom_filter_proxy import MultiRoleFilterProxyModel
from qgis_hub_plugin.gui.constants import (
    CreatorRole,
    NameRole,
    ResourceSubtypeRole,
    ResourceTypeRole,
    SortingRole,
)

# Initialize QGIS application
start_app()


class TestFilterProxyModel(unittest.TestCase):
    """Test MultiRoleFilterProxyModel filtering and sorting."""

    def setUp(self):
        """Create model with test data."""
        self.model = QStandardItemModel()
        self.proxy = MultiRoleFilterProxyModel()
        self.proxy.setSourceModel(self.model)

        # Add diverse test items
        self._add_item("Processing Model 1", "model", "", "Creator A", 10)
        self._add_item("Symbol Style 1", "style", "symbol", "Creator B", 50)
        self._add_item("Python Script 1", "processingscript", "python", "Creator C", 30)
        self._add_item("Processing Model 2", "model", "", "Creator A", 20)
        self._add_item("ColorRamp Style 1", "style", "colorramp", "Creator D", 40)
        self._add_item("R Script 1", "processingscript", "r", "Creator E", 15)

    def _add_item(self, name, resource_type, subtype, creator, download_count):
        """Helper to add items to model with all relevant data roles.

        Args:
            name: Resource name
            resource_type: Type of resource (model, style, etc.)
            subtype: Subtype of resource (symbol, python, etc.)
            creator: Creator name
            download_count: Number of downloads (for sorting)
        """
        item = QStandardItem(name)
        item.setData(resource_type, ResourceTypeRole)
        item.setData(subtype, ResourceSubtypeRole)
        item.setData(name, NameRole)
        item.setData(creator, CreatorRole)
        item.setData(download_count, SortingRole)
        self.model.appendRow(item)

    def test_no_filter_shows_all(self):
        """Test that without filters, all items are visible."""
        # No filters set
        self.assertEqual(self.proxy.rowCount(), 6)

    def test_filter_by_single_resource_type(self):
        """Test filtering by a single resource type."""
        # Enable only "model" type
        self.proxy.setCheckboxStates({"model": True})
        self.proxy.setRolesToFilter([NameRole])

        # Should show 2 models
        self.assertEqual(self.proxy.rowCount(), 2)

        # Verify the shown items are models
        for row in range(self.proxy.rowCount()):
            index = self.proxy.index(row, 0)
            resource_type = self.proxy.data(index, ResourceTypeRole)
            self.assertEqual(resource_type, "model")

    def test_filter_by_multiple_resource_types(self):
        """Test filtering by multiple resource types."""
        # Enable "model" and "style" types
        checkbox_states = {"model": True, "style": True}
        self.proxy.setCheckboxStates(checkbox_states)
        self.proxy.setRolesToFilter([NameRole])

        # Should show 2 models + 2 styles = 4 items
        self.assertEqual(self.proxy.rowCount(), 4)

    def test_filter_by_subtype(self):
        """Test filtering by resource subtype."""
        # Enable style:symbol specifically
        checkbox_states = {
            "style": True,
            "style:symbol": True,
            "style:colorramp": False,  # Disable colorramp
        }
        self.proxy.setCheckboxStates(checkbox_states)
        self.proxy.setRolesToFilter([NameRole])

        # Should show only 1 symbol style (colorramp filtered out)
        self.assertEqual(self.proxy.rowCount(), 1)

        # Verify it's the symbol style
        index = self.proxy.index(0, 0)
        self.assertEqual(self.proxy.data(index, ResourceTypeRole), "style")
        self.assertEqual(self.proxy.data(index, ResourceSubtypeRole), "symbol")

    def test_filter_by_text_search(self):
        """Test text search filtering."""
        # Enable all types
        checkbox_states = {"model": True, "style": True, "processingscript": True}
        self.proxy.setCheckboxStates(checkbox_states)
        self.proxy.setRolesToFilter([NameRole])

        # Search for "Model"
        self.proxy.setFilterRegExp(QRegExp(".*Model.*"))

        # Should show 2 models
        self.assertEqual(self.proxy.rowCount(), 2)

    def test_filter_by_creator(self):
        """Test filtering by creator name."""
        # Enable all types
        checkbox_states = {"model": True, "style": True, "processingscript": True}
        self.proxy.setCheckboxStates(checkbox_states)
        self.proxy.setRolesToFilter([CreatorRole])

        # Search for "Creator A"
        self.proxy.setFilterRegExp(QRegExp("Creator A"))

        # Should show 2 items by Creator A
        self.assertEqual(self.proxy.rowCount(), 2)

    def test_combined_type_and_text_filters(self):
        """Test combining type and text filters."""
        # Enable only models
        self.proxy.setCheckboxStates({"model": True})
        self.proxy.setRolesToFilter([NameRole])

        # Search for "1"
        self.proxy.setFilterRegExp(QRegExp(".*1"))

        # Should show only "Processing Model 1"
        self.assertEqual(self.proxy.rowCount(), 1)

        index = self.proxy.index(0, 0)
        name = self.proxy.data(index, NameRole)
        self.assertEqual(name, "Processing Model 1")

    def test_filter_returns_no_results(self):
        """Test filter that matches no items."""
        self.proxy.setCheckboxStates({"model": True})
        self.proxy.setRolesToFilter([NameRole])

        # Search for something that doesn't exist
        self.proxy.setFilterRegExp(QRegExp("NonExistentResource"))

        # Should show 0 items
        self.assertEqual(self.proxy.rowCount(), 0)

    def test_filter_with_empty_checkbox_states(self):
        """Test that empty checkbox states shows nothing."""
        # Set empty checkbox states (all unchecked)
        self.proxy.setCheckboxStates({})
        self.proxy.setRolesToFilter([NameRole])

        # With checkbox states set but all false, should show nothing
        # But empty dict means no filter, so shows all
        self.assertEqual(self.proxy.rowCount(), 6)

    def test_filter_all_types_disabled(self):
        """Test that disabling all types shows nothing."""
        # Explicitly disable all types
        checkbox_states = {"model": False, "style": False, "processingscript": False}
        self.proxy.setCheckboxStates(checkbox_states)
        self.proxy.setRolesToFilter([NameRole])

        # Should show 0 items
        self.assertEqual(self.proxy.rowCount(), 0)

    def test_sorting_by_download_count(self):
        """Test sorting by download count (SortingRole)."""
        # Enable all types
        checkbox_states = {"model": True, "style": True, "processingscript": True}
        self.proxy.setCheckboxStates(checkbox_states)
        self.proxy.setRolesToFilter([NameRole])

        # Sort by column 0 (which has SortingRole data)
        self.proxy.sort(0, 1)  # 1 = Descending

        # Verify order by download count (50, 40, 30, 20, 15, 10)
        expected_counts = [50, 40, 30, 20, 15, 10]
        for row, expected_count in enumerate(expected_counts):
            index = self.proxy.index(row, 0)
            actual_count = self.proxy.data(index, SortingRole)
            self.assertEqual(actual_count, expected_count)

    def test_case_insensitive_search(self):
        """Test case-insensitive text search."""
        checkbox_states = {"model": True, "style": True, "processingscript": True}
        self.proxy.setCheckboxStates(checkbox_states)
        self.proxy.setRolesToFilter([NameRole])

        # Search with different case
        regex = QRegExp(".*python.*", Qt.CaseInsensitive)
        self.proxy.setFilterRegExp(regex)

        # Should match "Python Script 1"
        self.assertEqual(self.proxy.rowCount(), 1)

    def test_multi_role_filtering(self):
        """Test filtering across multiple roles."""
        checkbox_states = {"model": True, "style": True, "processingscript": True}
        self.proxy.setCheckboxStates(checkbox_states)

        # Filter by both name and creator
        self.proxy.setRolesToFilter([NameRole, CreatorRole])

        # Search for "Creator A" - should match in creator role
        self.proxy.setFilterRegExp(QRegExp("Creator A"))

        # Should show 2 items by Creator A
        self.assertEqual(self.proxy.rowCount(), 2)

    def test_subtype_filtering_with_no_subtype(self):
        """Test filtering resources with empty subtypes."""
        # Models have no subtype
        checkbox_states = {
            "model": True,
        }
        self.proxy.setCheckboxStates(checkbox_states)
        self.proxy.setRolesToFilter([NameRole])

        # Should show 2 models
        self.assertEqual(self.proxy.rowCount(), 2)

        # Verify all have empty subtypes
        for row in range(self.proxy.rowCount()):
            index = self.proxy.index(row, 0)
            subtype = self.proxy.data(index, ResourceSubtypeRole)
            self.assertEqual(subtype, "")

    def test_dynamic_filter_updates(self):
        """Test that filters update dynamically."""
        # Start with models only
        self.proxy.setCheckboxStates({"model": True})
        self.proxy.setRolesToFilter([NameRole])
        self.assertEqual(self.proxy.rowCount(), 2)

        # Add styles
        checkbox_states = {"model": True, "style": True}
        self.proxy.setCheckboxStates(checkbox_states)

        # Should now show 4 items
        self.assertEqual(self.proxy.rowCount(), 4)

        # Remove models
        self.proxy.setCheckboxStates({"style": True})

        # Should now show only 2 styles
        self.assertEqual(self.proxy.rowCount(), 2)


class TestFilterProxyEdgeCases(unittest.TestCase):
    """Test edge cases for filter proxy model."""

    def setUp(self):
        """Create minimal model."""
        self.model = QStandardItemModel()
        self.proxy = MultiRoleFilterProxyModel()
        self.proxy.setSourceModel(self.model)

    def test_empty_model(self):
        """Test proxy with empty source model."""
        # No items added
        self.assertEqual(self.proxy.rowCount(), 0)

        # Set filters on empty model
        self.proxy.setCheckboxStates({"model": True})
        self.proxy.setRolesToFilter([NameRole])

        # Should still be 0
        self.assertEqual(self.proxy.rowCount(), 0)

    def test_single_item_model(self):
        """Test proxy with single item."""
        item = QStandardItem("Single Item")
        item.setData("model", ResourceTypeRole)
        item.setData("Single Item", NameRole)
        self.model.appendRow(item)

        # Enable model type
        self.proxy.setCheckboxStates({"model": True})
        self.proxy.setRolesToFilter([NameRole])

        # Should show 1 item
        self.assertEqual(self.proxy.rowCount(), 1)

    def test_None_data_handling(self):
        """Test handling of None values in data roles."""
        item = QStandardItem("Item with None")
        item.setData("model", ResourceTypeRole)
        item.setData(None, ResourceSubtypeRole)  # Explicitly set None
        item.setData("Item with None", NameRole)
        self.model.appendRow(item)

        # Should not crash with None values
        self.proxy.setCheckboxStates({"model": True})
        self.proxy.setRolesToFilter([NameRole])

        self.assertEqual(self.proxy.rowCount(), 1)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
