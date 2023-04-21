import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QSize, Qt
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
            item = ResourceItem(resource)
            self.resource_model.appendRow(item)


def shorten_string(text: str) -> str:
    if len(text) > 20:
        text = text[:17] + "..."
    return text


class ResourceItem(QStandardItem):
    def __init__(self, params: dict):
        super().__init__()

        # Attribute from the QGIS Hub
        self.resource_type = params.get("resource_type")
        self.uuid = params.get("uuid")
        self.name = params.get("name")
        self.creator = params.get("name")
        self.upload_time = params.get("upload_date")
        self.description = params.get("description")
        self.file = params.get("file")
        self.thumbnail = params.get("thumbnail")

        # Custom attribute
        self.setText(shorten_string(self.name))
        self.setToolTip(f"{self.name} by {self.creator}")
        # TODO(IS): Use different icon for different resource type or use the preview
        self.setIcon(get_icon("qbrowser_icon.svg"))
