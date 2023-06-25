import os
import zipfile
from datetime import datetime
from pathlib import Path

from qgis.core import Qgis, QgsApplication, QgsProject, QgsSettings, QgsVectorLayer
from qgis.gui import QgsMessageBar
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QRegExp, QSize, Qt, QUrl, pyqtSlot
from qgis.PyQt.QtGui import (
    QDesktopServices,
    QIcon,
    QPixmap,
    QStandardItem,
    QStandardItemModel,
)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QFileDialog,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QSizePolicy,
)

from qgis_hub_plugin.core.api_client import get_all_resources
from qgis_hub_plugin.core.custom_filter_proxy import MultiRoleFilterProxyModel
from qgis_hub_plugin.toolbelt import PlgLogger
from qgis_hub_plugin.utilities.common import download_file, get_icon
from qgis_hub_plugin.utilities.qgis_util import show_busy_cursor

UI_CLASS = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "resource_browser.ui")
)[0]


def store_settings(key_value, stored_value):
    s = QgsSettings()
    # s.setValue("myplugin/downloadLocation", download_location)
    s.setValue(key_value, stored_value)


def read_settings(key_value, stored_value):
    s = QgsSettings()
    download_location = s.value(key_value, defaultValue=stored_value)
    # download_location = s.value(
    #     "myplugin/downloadLocation", defaultValue=default_download_location
    # )
    return download_location


class ResourceBrowserDialog(QDialog, UI_CLASS):
    def __init__(self, parent=None, iface=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.parent = parent
        self.iface = iface
        self.log = PlgLogger().log

        self.graphicsScene = QGraphicsScene()
        self.graphicsViewPreview.setScene(self.graphicsScene)

        # Message bar
        self.message_bar = QgsMessageBar(self)
        self.message_bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.vlayout.insertWidget(0, self.message_bar)

        # Resources
        self.resources = []
        self.checkbox_states = {}
        self.update_checkbox_states()
        self.resource_model = QStandardItemModel(self.listViewResources)

        self.proxy_model = MultiRoleFilterProxyModel()
        self.proxy_model.setSourceModel(self.resource_model)
        self.listViewResources.setModel(self.proxy_model)

        self.resource_selection_model = self.listViewResources.selectionModel()
        self.resource_selection_model.selectionChanged.connect(
            self.on_resource_selection_changed
        )

        # TODO(IS): make user able to change the icon size
        self.listViewResources.setIconSize(QSize(96, 96))

        # Load resource for the first time
        self.populate_resources()

        self.lineEditSearch.textChanged.connect(self.on_filter_text_changed)

        self.pushButtonDownload.clicked.connect(self.download_resource)

        self.addQGISPushButton.clicked.connect(self.add_to_qgis)

        self.checkBoxGeopackage.stateChanged.connect(self.update_resource_filter)
        self.checkBoxStyle.stateChanged.connect(self.update_resource_filter)
        self.checkBoxModel.stateChanged.connect(self.update_resource_filter)

        self.reloadPushButton.clicked.connect(
            lambda: self.populate_resources(force_update=True)
        )

        self.hide_preview()

    def show_success_message(self, text):
        return self.message_bar.pushMessage(
            self.tr("Success"), self.tr(text), Qgis.Success, 5
        )

    def show_warning_message(self, text):
        return self.message_bar.pushMessage(
            self.tr("Warning"), self.tr(text), Qgis.Warning, 5
        )

    @show_busy_cursor
    def populate_resources(self, force_update=False):
        if force_update or not self.resources:
            response = get_all_resources(force_update=force_update)

            if response is None:
                self.show_warning_message("Error populating the resources")
                return

            self.resources = response.get("results", {})

        self.resource_model.clear()
        for resource in self.resources:
            item = ResourceItem(resource)
            self.resource_model.appendRow(item)

        if force_update:
            self.show_success_message("Successfully populated the resources")

        self.update_title_bar()

    def update_checkbox_states(self):
        geopackage_checked = self.checkBoxGeopackage.isChecked()
        style_checked = self.checkBoxStyle.isChecked()
        model_checked = self.checkBoxModel.isChecked()

        self.checkbox_states = {
            "Geopackage": geopackage_checked,
            "Style": style_checked,
            "Model": model_checked,
        }

    def update_resource_filter(self):
        current_text = self.lineEditSearch.text()

        self.update_checkbox_states()

        filter_regexp_parts = ["NONE"]
        for resource_type, checked in self.checkbox_states.items():
            if checked:
                filter_regexp_parts.append(resource_type)

        filter_regexp = QRegExp("|".join(filter_regexp_parts), Qt.CaseInsensitive)
        self.proxy_model.setFilterRegExp(filter_regexp)
        self.proxy_model.setRolesToFilter([ResourceItem.ResourceTypeRole])
        self.proxy_model.setCheckboxStates(self.checkbox_states)
        self.on_filter_text_changed(current_text)

    def on_filter_text_changed(self, text):
        self.proxy_model.setFilterRegExp(QRegExp(text, Qt.CaseInsensitive))
        self.proxy_model.setRolesToFilter(
            [ResourceItem.NameRole, ResourceItem.CreatorRole]
        )
        self.proxy_model.setCheckboxStates(self.checkbox_states)

        self.update_title_bar()

    @pyqtSlot("QItemSelection", "QItemSelection")
    def on_resource_selection_changed(self, selected, deselected):
        if self.selected_resource():
            self.update_preview()
        else:
            self.log("no resource selected")

    def selected_resource(self):
        selected_indexes = self.listViewResources.selectionModel().selectedIndexes()
        if len(selected_indexes) > 0:
            proxy_index = selected_indexes[0]
            source_index = self.proxy_model.mapToSource(proxy_index)
            return self.resource_model.itemFromIndex(source_index)
        else:
            return None

    def update_preview(self):
        # import pydevd_pycharm
        # pydevd_pycharm.settrace('127.0.0.1', port=53100, stdoutToServer=True, stderrToServer=True)
        resource = self.selected_resource()
        if resource is None:
            self.hide_preview()
            return
        self.show_preview()

        if resource.resource_type == "Model":
            self.addQGISPushButton.setText("Add to QGIS")
            self.addQGISPushButton.setVisible(True)
        elif resource.resource_type == "Geopackage":
            self.addQGISPushButton.setText("Add to Current Project")
            self.addQGISPushButton.setVisible(True)
        else:
            self.addQGISPushButton.setVisible(False)

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
        if resource.resource_subtype:
            self.labelSubtype.setText(resource.resource_subtype)
        self.labelCreator.setText(resource.creator)
        self.labelDownloadCount.setText(str(resource.download_count))
        pretty_upload_date = resource.upload_date.strftime("%-d %B %Y")
        self.labelUploaded.setText(pretty_upload_date)
        self.textBrowserDescription.setHtml(resource.description)

    def hide_preview(self):
        self.groupBoxPreview.hide()

    def show_preview(self):
        self.groupBoxPreview.show()

    def download_resource(self):
        resource = self.selected_resource()
        file_extension = os.path.splitext(resource.file)[1]

        # Set the default download location
        default_download_location = "~/Downloads"

        # Read the stored download location
        download_location = read_settings(
            "myplugin/downloadLocation", default_download_location
        )

        default_path = os.path.join(download_location, os.path.basename(resource.file))

        file_path = QFileDialog.getSaveFileName(
            self,
            self.tr("Save Resource"),
            default_path,
            self.tr(
                "All Files (*);;Geopackage (*.gpkg);;QGIS Model (*.model3);; ZIP Files (*.zip)"
            ),
        )[0]

        if file_path:
            if not file_path.endswith(file_extension):
                file_path = file_path + file_extension

            if not download_resource_file(resource.file, file_path):
                self.show_warning_message(f"Download failed for {resource.name}")
            else:
                self.show_success_message(f"Downloaded {resource.name} to {file_path}")

                if self.checkBoxOpenDirectory.isChecked():
                    QDesktopServices.openUrl(
                        QUrl.fromLocalFile(str(Path(file_path).parent))
                    )

                store_settings("myplugin/downloadLocation", str(Path(file_path).parent))

    def add_to_qgis(self):
        resource = self.selected_resource()
        if resource.resource_type == "Model":
            self.add_model_to_qgis()
        elif resource.resource_type == "Geopackage":
            self.add_geopackage()

    def add_model_to_qgis(self):
        resource = self.selected_resource()
        qgis_user_dir = QgsApplication.qgisSettingsDirPath()
        default_model_path = Path(qgis_user_dir, "processing", "models")
        if not default_model_path.exists():
            default_model_path.mkdir(parents=True, exist_ok=True)

        default_model_path = os.path.join(
            default_model_path, os.path.basename(resource.file)
        )

        file_path = QFileDialog.getSaveFileName(
            self,
            self.tr("Save Model"),
            str(default_model_path),
            self.tr("QGIS Model (*.model3)"),
        )[0]

        if file_path:
            if not download_resource_file(resource.file, file_path):
                self.show_warning_message(f"Download failed for {resource.name}")
            else:
                self.show_success_message(
                    f"Successfully downloaded {resource.name} to {file_path}"
                )

            # Refreshing the processing toolbox
            QgsApplication.processingRegistry().providerById(
                "model"
            ).refreshAlgorithms()

    def add_geopackage(self):
        resource = self.selected_resource()
        file_extension = os.path.splitext(resource.file)[1]

        file_path = QFileDialog.getSaveFileName(
            self,
            self.tr("Save Resource"),
            resource.file,
            self.tr("ZIP Files (*.zip)"),
        )[0]

        if file_path:
            if not file_path.endswith(file_extension):
                file_path = file_path + file_extension

            if not download_resource_file(resource.file, file_path):
                self.show_warning_message(f"Download failed for {resource.name}")

        # Extract the geopackage file from the zip
        if file_path.endswith(".zip"):
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                for filename in zip_ref.namelist():
                    if filename.endswith(".gpkg"):
                        geopackage_filename = os.path.basename(filename)
                        extract_location = os.path.dirname(file_path)
                        zip_ref.extract(filename, extract_location)
                        break
        else:
            geopackage_filename = os.path.basename(file_path)
            extract_location = os.path.dirname(file_path)

        current_project = QgsProject.instance()
        layer_path = os.path.join(extract_location, geopackage_filename)
        geopackage = QgsVectorLayer(layer_path, geopackage_filename, "ogr")
        if geopackage.isValid():
            # Add all layers from the geopackage to the project
            layers = geopackage.dataProvider().subLayers()
            for layer in layers:
                layer_parts = layer.split("!!::!!")
                layer_name = layer_parts[1]
                layer_uri = f"{layer_path}|layername={layer_name}"
                vector_layer = QgsVectorLayer(layer_uri, layer_name, "ogr")
                if vector_layer.isValid():
                    current_project.addMapLayer(vector_layer)
                else:
                    self.show_warning_message("Invalid layer:", layer_name)
        else:
            self.show_warning_message("Invalid geopackage:", layer_path)

        self.show_success_message("Geopackage successfully added to current project")

    def update_title_bar(self):
        num_total_resources = len(self.resources)
        num_selected_resources = self.proxy_model.rowCount()
        window_title = self.tr(
            f"QGIS Hub Explorer ({num_selected_resources} of {num_total_resources})"
        )
        self.setWindowTitle(window_title)


# TODO: do it QGIS task to have
def download_resource_file(url: str, file_path: str):
    resource_path = Path(file_path)
    download_file(url, resource_path)
    if resource_path.exists():
        return resource_path
    else:
        return None


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
    ResourceTypeRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    CreatorRole = Qt.UserRole + 3

    def __init__(self, params: dict):
        super().__init__()

        # Attribute from the QGIS Hub
        self.resource_type = params.get("resource_type")
        self.resource_subtype = params.get("resource_subtype", "")
        self.uuid = params.get("uuid")
        self.name = params.get("name")
        self.creator = params.get("creator")
        upload_date_string = params.get("upload_date")
        self.upload_date = datetime.fromisoformat(upload_date_string)
        self.download_count = params.get("download_count")
        self.description = params.get("description")
        self.file = params.get("file")
        self.thumbnail = params.get("thumbnail")

        # Custom attribute
        self.setText(shorten_string(self.name))
        self.setToolTip(f"{self.name} by {self.creator}")
        thumbnail_path = download_resource_thumbnail(self.thumbnail, self.uuid)
        if thumbnail_path:
            self.setIcon(QIcon(str(thumbnail_path)))
        else:
            self.setIcon(get_icon("qbrowser_icon.svg"))

        self.setData(self.resource_type, self.ResourceTypeRole)
        self.setData(self.name, self.NameRole)
        self.setData(self.creator, self.CreatorRole)
