import os
from pathlib import Path

from qgis.core import Qgis, QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QSize, Qt, pyqtSlot
from qgis.PyQt.QtGui import QPixmap, QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import QDialog, QGraphicsPixmapItem, QGraphicsScene

from qgis_hub_plugin.core.api_client import get_all_resources
from qgis_hub_plugin.toolbelt import PlgLogger
from qgis_hub_plugin.utilities.common import download_file, get_icon

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

        self.graphicsScene = QGraphicsScene()
        self.graphicsViewPreview.setScene(self.graphicsScene)

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

        self.pushButtonDownload.clicked.connect(self.download_resource)

        self.hide_preview()

    def populate_resources(self):
        response = get_all_resources()
        # total = response.get("total")
        # previous_url = response.get("previous")
        # next_url = response.get("next")
        resources = response.get("results", {})

        for resource in resources:
            item = ResourceItem(resource)
            self.resource_model.appendRow(item)

    @pyqtSlot("QItemSelection", "QItemSelection")
    def on_resource_selecton_changed(self, selected, deselected):
        if self.selected_resource():
            self.update_preview()
        else:
            self.log("no resource selected")

    def selected_resource(self):
        selected_indexes = self.listViewResources.selectionModel().selectedIndexes()
        if len(selected_indexes) > 0:
            return self.resource_model.itemFromIndex(selected_indexes[0])
        else:
            return None

    def update_preview(self):
        resource = self.selected_resource()
        if resource is None:
            self.hide_preview()
            return
        self.show_preview()

        # Thumbnail
        thumbnail_path = download_resource_thumbnail(resource.thumbnail, resource.uuid)
        pixmap = QPixmap(str(thumbnail_path.absolute()))
        if not pixmap.isNull():
            item = QGraphicsPixmapItem(pixmap)

        self.graphicsViewPreview.scene().clear()
        self.graphicsViewPreview.scene().addItem(item)
        self.graphicsViewPreview.fitInView(item, Qt.KeepAspectRatio)

        # Description
        self.labelName.setText(resource.name)
        self.labelType.setText(resource.resource_type)
        self.labelSubtype.setVisible(bool(resource.resource_subtype))
        self.labelSubtypeLabel.setVisible(bool(resource.resource_subtype))
        if not resource.resource_subtype:
            self.labelSubtype.setText(resource.resource_subtype)
        self.labelCreator.setText(resource.creator)
        self.textBrowserDescription.setHtml(resource.description)

    def hide_preview(self):
        self.groupBoxPreview.hide()

    def show_preview(self):
        self.groupBoxPreview.show()

    def download_resource(self):
        resource = self.selected_resource()
        file_path = download_resource_file(
            resource.file, resource.resource_type, resource.uuid
        )
        if file_path:
            text = f"Successfully download {resource.name} to {file_path}"
            self.iface.messageBar().pushMessage(self.tr("Success"), text, duration=5)
        else:
            text = f"Failed download {resource.name} from {resource.file}"
            self.iface.messageBar().pushMessage(
                self.tr("Warning"), text, level=Qgis.Warning, duration=5
            )


# TODO: do it QGIS task to have
def download_resource_file(url: str, resource_type: str, uuid: str):
    qgis_user_dir = QgsApplication.qgisSettingsDirPath()
    download_dir = Path(qgis_user_dir, "qgis_hub", "downloads", resource_type)
    file_name = url.split("/")[-1]
    resource_path = Path(download_dir, file_name)
    if not download_dir.exists():
        download_dir.mkdir(parents=True, exist_ok=True)

    download_file(url, resource_path)
    if resource_path.exists():
        return resource_path


def download_resource_thumbnail(url: str, uuid: str):
    qgis_user_dir = QgsApplication.qgisSettingsDirPath()
    # Assume it as jpg
    extension = ".jpg"
    try:
        extension = url.split(".")[-1]
    except IndexError():
        pass

    thumbnail_dir = Path(qgis_user_dir, "qgis_hub", "thumbnails")
    thumbnail_path = Path(thumbnail_dir, f"{uuid}.{extension}")
    if not thumbnail_dir.exists():
        thumbnail_dir.mkdir(parents=True, exist_ok=True)

    download_file(url, thumbnail_path)
    if thumbnail_path.exists():
        return thumbnail_path


def shorten_string(text: str) -> str:
    if len(text) > 20:
        text = text[:17] + "..."
    return text


class ResourceItem(QStandardItem):
    def __init__(self, params: dict):
        super().__init__()

        # Attribute from the QGIS Hub
        self.resource_type = params.get("resource_type")
        self.resource_subtype = params.get("resource_subtype", "")
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
        # TODO(IS): Use different icon for different resource type or use the thumbnail
        self.setIcon(get_icon("qbrowser_icon.svg"))
