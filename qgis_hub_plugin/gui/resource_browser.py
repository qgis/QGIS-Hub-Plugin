import os

import requests
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QSize, Qt, pyqtSlot
from qgis.PyQt.QtGui import QPixmap, QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import QDialog

from qgis_hub_plugin.core.api_client import get_all_resources
from qgis_hub_plugin.toolbelt import PlgLogger
from qgis_hub_plugin.utilities.common import download_image, get_icon

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

        self.resource_selection_model = self.listViewResources.selectionModel()
        self.resource_selection_model.selectionChanged.connect(
            self.on_resource_selecton_changed
        )
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

    @pyqtSlot("QItemSelection", "QItemSelection")
    def on_resource_selecton_changed(self, selected, deselected):
        if self.selected_resource():
            selected_resource = self.selected_resource()
            self.update_preview()
            self.log(f"selected resource: {selected_resource.name}")
        else:
            # No construction phase is selected thus remove all selection of main cable
            self.log("no resource selected")

    def selected_resource(self):
        selected_indexes = self.listViewResources.selectionModel().selectedIndexes()
        if len(selected_indexes) > 0:
            return self.resource_model.itemFromIndex(selected_indexes[0])

    def update_preview(self):
        selected_resource = self.selected_resource()
        # Thumbnail
        # TODO: save it as a file (caching)
        image_path = f"/home/ismailsunni/Downloads/{selected_resource.uuid}.{selected_resource.thumbnail.split('.')[-1]}"
        self.log(image_path)

        if not os.path.exists(image_path):
            download_image(
                selected_resource.thumbnail,
                image_path,
            )

        # data = requests.get(selected_resource.thumbnail)
        pixmap = QPixmap()
        pixmap.load(image_path)
        pixmap.scaled(256, 256, Qt.KeepAspectRatio)
        # pixmap.loadFromData(data.content)
        self.labelIResourcePreview.setPixmap(pixmap)

        # Description


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
