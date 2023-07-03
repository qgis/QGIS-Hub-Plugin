import os
import platform
import tempfile
from pathlib import Path

from qgis.core import Qgis, QgsApplication, QgsStyle
from qgis.gui import QgsMessageBar
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QRegExp, QSize, Qt, QUrl, pyqtSlot
from qgis.PyQt.QtGui import QDesktopServices, QIcon, QPixmap, QStandardItemModel
from qgis.PyQt.QtWidgets import (
    QDialog,
    QFileDialog,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QSizePolicy,
)

from qgis_hub_plugin.core.api_client import get_all_resources
from qgis_hub_plugin.core.custom_filter_proxy import MultiRoleFilterProxyModel
from qgis_hub_plugin.gui.constants import (
    CreatorRole,
    NameRole,
    ResourceTypeRole,
    ResoureType,
)
from qgis_hub_plugin.gui.resource_item import ResourceItem
from qgis_hub_plugin.toolbelt import PlgLogger
from qgis_hub_plugin.utilities.common import download_file, download_resource_thumbnail
from qgis_hub_plugin.utilities.qgis_util import show_busy_cursor

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

        # Buttons
        self.listViewToolButton.setIcon(
            QgsApplication.getThemeIcon("mActionOpenTable.svg"),
        )
        self.iconViewToolButton.setIcon(
            QgsApplication.getThemeIcon("mActionIconView.svg"),
        )

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
        self.resource_model = QStandardItemModel()

        self.proxy_model = MultiRoleFilterProxyModel()
        self.proxy_model.setSourceModel(self.resource_model)

        self.listViewResources.setModel(self.proxy_model)
        self.treeViewResources.setModel(self.proxy_model)

        self.listViewResources.selectionModel().selectionChanged.connect(
            self.on_resource_selection_changed
        )
        self.treeViewResources.selectionModel().selectionChanged.connect(
            self.on_resource_selection_changed
        )

        # TODO(IS): make user able to change the icon size
        self.listViewResources.setIconSize(QSize(96, 96))

        # Load resource for the first time
        self.populate_resources()

        self.lineEditSearch.textChanged.connect(self.on_filter_text_changed)

        self.pushButtonDownload.clicked.connect(self.download_resource)

        self.addQGISPushButton.clicked.connect(self.add_resource_to_qgis)

        self.checkBoxGeopackage.stateChanged.connect(self.update_resource_filter)
        self.checkBoxStyle.stateChanged.connect(self.update_resource_filter)
        self.checkBoxModel.stateChanged.connect(self.update_resource_filter)

        self.listViewToolButton.toggled.connect(self.show_list_view)
        self.iconViewToolButton.toggled.connect(self.show_icon_view)

        self.reloadPushButton.clicked.connect(
            lambda: self.populate_resources(force_update=True)
        )

        self.hide_preview()

    def show_success_message(self, text):
        return self.message_bar.pushMessage(self.tr("Success"), text, Qgis.Success, 5)

    def show_error_message(self, text):
        return self.message_bar.pushMessage(self.tr("Error"), text, Qgis.Critical, 5)

    def show_warning_message(self, text):
        return self.message_bar.pushMessage(self.tr("Warning"), text, Qgis.Warning, 5)

    @show_busy_cursor
    def populate_resources(self, force_update=False):
        if force_update or not self.resources:
            response = get_all_resources(force_update=force_update)

            if response is None:
                self.show_warning_message("Error populating the resources")
                return

            self.resources = response.get("results", {})

        self.resource_model.clear()
        # TODO: Make sure it also show other attribute
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
            ResoureType.Geopackage: geopackage_checked,
            ResoureType.Style: style_checked,
            ResoureType.Model: model_checked,
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
        self.proxy_model.setRolesToFilter([ResourceTypeRole])
        self.proxy_model.setCheckboxStates(self.checkbox_states)
        self.on_filter_text_changed(current_text)

    def on_filter_text_changed(self, text):
        self.proxy_model.setFilterRegExp(QRegExp(text, Qt.CaseInsensitive))
        self.proxy_model.setRolesToFilter([NameRole, CreatorRole])
        self.proxy_model.setCheckboxStates(self.checkbox_states)

        self.update_title_bar()

    @pyqtSlot("QItemSelection", "QItemSelection")
    def on_resource_selection_changed(self, selected, deselected):
        if self.selected_resource():
            self.update_preview()
            self.update_custom_button()
        else:
            self.log("no resource selected")

    def selected_resource(self):
        # TODO: Check mode grid or list, and probably updated the selected resource on other view
        selected_indexes = self.listViewResources.selectionModel().selectedIndexes()
        if len(selected_indexes) > 0:
            proxy_index = selected_indexes[0]
            source_index = self.proxy_model.mapToSource(proxy_index)
            return self.resource_model.itemFromIndex(source_index)
        else:
            return None

    def update_custom_button(self):
        self.addQGISPushButton.setVisible(True)
        if self.selected_resource().resource_type == ResoureType.Model:
            self.addQGISPushButton.setText(self.tr("Add Model to QGIS"))
        elif self.selected_resource().resource_type == ResoureType.Style:
            self.addQGISPushButton.setText(self.tr("Add Style to QGIS"))
        else:
            self.addQGISPushButton.setVisible(False)

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

        file_path = QFileDialog.getSaveFileName(
            self,
            self.tr("Save Resource"),
            resource.file,
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

    def add_resource_to_qgis(self):
        if self.selected_resource().resource_type == "Model":
            self.add_model_to_qgis()
        elif self.selected_resource().resource_type == "Style":
            self.add_style_to_qgis()

    @show_busy_cursor
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
            if download_resource_file(resource.file, file_path):
                self.show_success_message(
                    self.tr(f"Model {resource.name} is added to QGIS")
                )

            else:
                self.show_warning_message(
                    self.tr(f"Download failed for model {resource.name}")
                )

            # Refreshing the processing toolbox
            QgsApplication.processingRegistry().providerById(
                "model"
            ).refreshAlgorithms()

    @show_busy_cursor
    def add_style_to_qgis(self):
        resource = self.selected_resource()
        tempdir = Path(
            "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()
        )
        tempfile_path = Path(tempdir, resource.file.split("/")[-1])
        download_resource_file(resource.file, tempfile_path, True)

        # Add to QGIS style library
        style = QgsStyle().defaultStyle()
        result = style.importXml(str(tempfile_path.absolute()))
        if result:
            self.show_success_message(
                self.tr(f"Style {resource.name} is added to QGIS")
            )
        else:
            self.show_error_message(
                self.tr(f"Style {resource.name} is not added to QGIS")
            )

    def update_title_bar(self):
        num_total_resources = len(self.resources)
        num_selected_resources = self.proxy_model.rowCount()
        window_title = self.tr(
            f"QGIS Hub Explorer ({num_selected_resources} of {num_total_resources})"
        )
        self.setWindowTitle(window_title)

    def show_list_view(self):
        self.viewStackedWidget.setCurrentIndex(1)

    def show_icon_view(self):
        self.viewStackedWidget.setCurrentIndex(0)


# TODO: do it QGIS task to have
def download_resource_file(url: str, file_path: str, force: bool = False):
    resource_path = Path(file_path)
    download_file(url, resource_path, force)
    if resource_path.exists():
        return resource_path
    else:
        return None
