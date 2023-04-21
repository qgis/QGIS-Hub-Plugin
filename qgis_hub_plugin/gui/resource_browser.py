import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import QDialog

from qgis_hub_plugin.core.api_client import get_all_resources
from qgis_hub_plugin.toolbelt import PlgLogger
from qgis_hub_plugin.utilities.common import get_icon

UI_CLASS = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "resource_browser.ui")
)[0]


class ResourceBrowserDialog(QDialog, UI_CLASS):
    def __init__(self, parent=None, iface=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.parent = parent
        self.iface = iface
        self.log = PlgLogger().log

        # Resources
        self.resource_model = QStandardItemModel(self.listViewResources)
        self.listViewResources.setModel(self.resource_model)
        # TODO(IS): make user able to change the icon size
        self.listViewResources.setIconSize(QSize(96, 96))

        # Load resource for the first time
        self.populate_resources()

    def populate_resources(self):
        response = get_all_resources()
        total = response.get("total")
        previous_url = response.get("previous")
        next_url = response.get("next")
        resources = response.get("results", {})
        self.log(f"{total}, {previous_url}, {next_url}")

        for resource in resources:
            item = _create_resource_item(resource)
            self.resource_model.appendRow(item)


def shorten_string(text: str) -> str:
    if len(text) > 20:
        text = text[:17] + "..."
    return text


def _create_resource_item(params: dict):
    name = shorten_string(params.get("name"))
    item = QStandardItem(name)
    item.setToolTip(f'{params.get("name")} by {params.get("creator")}')
    # TODO(IS): Use different icon for different resource type or use the preview
    item.setIcon(get_icon("qbrowser_icon.svg"))
    return item
