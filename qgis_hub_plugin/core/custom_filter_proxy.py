from qgis.PyQt.QtCore import QSortFilterProxyModel

from qgis_hub_plugin.gui.constants import ResourceSubtypeRole, ResourceTypeRole, SortingRole
from qgis_hub_plugin.toolbelt import PlgLogger


class MultiRoleFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.roles_to_filter = []
        self.checkbox_states = {}
        self.log = PlgLogger().log

    # Custom sorting by integer
    def lessThan(self, left_index, right_index):
        left_data = left_index.data(SortingRole)
        right_data = right_index.data(SortingRole)

        if left_data is None or right_data is None:
            return super().lessThan(left_index, right_index)

        try:
            return left_data < right_data

        except ValueError:
            return super().lessThan(left_index, right_index)

    def setRolesToFilter(self, roles):
        self.roles_to_filter = roles
        self.invalidateFilter()

    def setCheckboxStates(self, checkbox_states):
        self.checkbox_states = checkbox_states
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        if not self.roles_to_filter or not self.checkbox_states:
            return True

        index = model.index(source_row, 0, source_parent)
        resource_type = model.data(index, ResourceTypeRole)
        resource_subtype = model.data(index, ResourceSubtypeRole)

        # Check if the resource type is enabled
        if not self.checkbox_states.get(resource_type, False):
            return False
        
        # Handle subtype filtering
        if resource_subtype:
            # Check if there's a specific filter for this type+subtype combination
            subtype_key = f"{resource_type}:{resource_subtype}"
            
            # If we have a specific filter for this subtype and it's False, filter it out
            if subtype_key in self.checkbox_states and not self.checkbox_states[subtype_key]:
                return False
        
        # Text search filtering
        for role in self.roles_to_filter:
            data = model.data(index, role)
            if data and self.filterRegExp().indexIn(str(data)) != -1:
                return True

        # If we're filtering by roles and nothing matched, hide the item
        if self.roles_to_filter:
            return False
        
        # Default to showing the item if no other filters applied
        return True
