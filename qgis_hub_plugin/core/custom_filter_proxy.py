from qgis.PyQt.QtCore import QSortFilterProxyModel, Qt

from qgis_hub_plugin.gui.constants import ResourceTypeRole
from qgis_hub_plugin.toolbelt import PlgLogger


class MultiRoleFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.roles_to_filter = []
        self.checkbox_states = {}
        self.log = PlgLogger().log

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

        if not self.checkbox_states.get(resource_type, False):
            return False

        for role in self.roles_to_filter:
            data = model.data(index, role)
            if self.filterRegExp().indexIn(data) != -1:
                return True

        return False
