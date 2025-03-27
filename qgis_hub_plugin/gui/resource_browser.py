import os
import platform
import tempfile
import zipfile
from functools import partial
from pathlib import Path

from qgis.core import (
    Qgis,
    QgsApplication,
    QgsLayerDefinition,
    QgsProject,
    QgsStyle,
    QgsVectorLayer,
)
from qgis.gui import QgsMessageBar
from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    QByteArray,
    QItemSelectionModel,
    QRegExp,
    QSize,
    Qt,
    QUrl,
    pyqtSlot,
)
from qgis.PyQt.QtGui import QDesktopServices, QPixmap, QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QSizePolicy,
    QTreeWidgetItem,
)

from qgis_hub_plugin.__about__ import __uri_homepage__
from qgis_hub_plugin.core.api_client import get_all_resources
from qgis_hub_plugin.core.custom_filter_proxy import MultiRoleFilterProxyModel
from qgis_hub_plugin.gui.constants import (
    CreatorRole,
    NameRole,
    ResourceTypeRole,
    ResoureType,
)
from qgis_hub_plugin.gui.resource_item import AttributeSortingItem, ResourceItem
from qgis_hub_plugin.toolbelt import PlgLogger, PlgOptionsManager
from qgis_hub_plugin.utilities.common import (
    QGIS_HUB_DIR,
    download_file,
    download_resource_thumbnail,
)
from qgis_hub_plugin.utilities.exception import DownloadError
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
        self.plg_settings = PlgOptionsManager()

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
        self.selected_resource = None
        self.filter_states = {}
        self.update_filter_states()

        # Setup resource model and proxy model first
        self.resource_model = QStandardItemModel()
        self.proxy_model = MultiRoleFilterProxyModel()
        self.proxy_model.setSourceModel(self.resource_model)

        # Now setup tree widget which depends on proxy_model
        self.setup_resource_type_tree()

        self.listViewResources.setModel(self.proxy_model)
        self.treeViewResources.setModel(self.proxy_model)
        self.treeViewResources.setSortingEnabled(True)

        # Load resource for the first time
        self.populate_resources()

        # Tooltip
        self.buttonBox.button(QDialogButtonBox.Help).setToolTip(
            self.tr("Open the help page")
        )
        self.listViewToolButton.setToolTip(self.tr("List view"))
        self.iconViewToolButton.setToolTip(self.tr("Icon view"))
        self.iconSizeSlider.setToolTip(self.tr("Thumbnail size"))
        self.checkBoxOpenDirectory.setToolTip(
            self.tr("Enable this to open the download directory after download")
        )
        self.reloadPushButton.setToolTip(
            self.tr("Update resources from the QGIS Hub website")
        )
        self.lineEditSearch.setToolTip(
            self.tr("Search resource by the name or the creator")
        )
        self.pushButtonDownload.setToolTip(
            self.tr("Download selected resource to your local disk")
        )

        # Signal handler
        self.lineEditSearch.textChanged.connect(self.on_filter_text_changed)

        self.listViewResources.selectionModel().selectionChanged.connect(
            self.on_resource_selection_changed
        )
        self.treeViewResources.selectionModel().selectionChanged.connect(
            self.on_resource_selection_changed
        )

        self.pushButtonDownload.clicked.connect(self.download_resource)
        self.addQGISPushButton.clicked.connect(self.add_resource_to_qgis)
        self.listViewToolButton.toggled.connect(self.show_list_view)
        self.iconViewToolButton.toggled.connect(self.show_icon_view)
        self.buttonBox.button(QDialogButtonBox.Help).clicked.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
        )
        self.reloadPushButton.clicked.connect(
            lambda: self.populate_resources(force_update=True)
        )
        self.buttonBox.rejected.connect(self.store_setting)

        # Match with the size of the thumbnail
        self.iconSizeSlider.setMinimum(20)
        self.iconSizeSlider.setMaximum(128)
        self.iconSizeSlider.valueChanged.connect(self.update_icon_size)

        self.restore_setting()
        self.hide_preview()

    def closeEvent(self, event):
        self.store_setting()
        super().closeEvent(event)

    def show_success_message(self, text):
        return self.message_bar.pushMessage(self.tr("Success"), text, Qgis.Success, 5)

    def show_error_message(self, text):
        return self.message_bar.pushMessage(self.tr("Error"), text, Qgis.Critical, 5)

    def show_warning_message(self, text):
        return self.message_bar.pushMessage(self.tr("Warning"), text, Qgis.Warning, 5)

    def store_setting(self):
        # Download directory check box
        self.plg_settings.set_value_from_key(
            "download_checkbox", self.checkBoxOpenDirectory.isChecked()
        )

        # Value in iconSizeSlider
        self.plg_settings.set_value_from_key("icon_size", self.iconSizeSlider.value())

        # List or grid view
        self.plg_settings.set_value_from_key(
            "current_view_index", self.viewStackedWidget.currentIndex()
        )

        # Geometry
        self.plg_settings.set_value_from_key("dialog_geometry", self.saveGeometry())

    def restore_setting(self):
        # Download directory check box
        self.checkBoxOpenDirectory.setChecked(
            self.plg_settings.get_value_from_key("download_checkbox", True, bool)
        )

        # Value in iconSizeSlider
        middle_value = int(
            self.iconSizeSlider.minimum()
            + (self.iconSizeSlider.maximum() - self.iconSizeSlider.minimum()) / 2
        )
        self.iconSizeSlider.setValue(
            self.plg_settings.get_value_from_key("icon_size", middle_value, int)
        )

        # List or grid view
        current_view_index = self.plg_settings.get_value_from_key(
            "current_view_index", 0, int
        )
        self.viewStackedWidget.setCurrentIndex(current_view_index)
        # May be there is a better way to do this
        self.iconViewToolButton.setChecked(current_view_index == 0)
        self.listViewToolButton.setChecked(current_view_index == 1)

        # Geometry
        geometry = self.plg_settings.get_value_from_key(
            "dialog_geometry", None, QByteArray
        )
        if geometry is not None:
            self.restoreGeometry(geometry)

    @show_busy_cursor
    def populate_resources(self, force_update=False):
        self.log(f"Populating resources {force_update}")
        if force_update or not self.resources:
            response = get_all_resources(force_update=force_update)

            if response is None:
                self.show_warning_message("Error populating the resources")
                return

            self.resources = response.get("results", {})

        self.resource_model.clear()
        self.resource_model.setHorizontalHeaderLabels(
            ["Name", "Creator", "Download", "Uploaded"]
        )
        for resource in self.resources:
            item = ResourceItem(resource)
            author = QStandardItem(item.creator)
            download_count = AttributeSortingItem(
                str(item.download_count), item.download_count
            )
            pretty_date = item.upload_date.strftime("%d %B %Y").lstrip("0")
            upload_date = AttributeSortingItem(pretty_date, item.upload_date)
            self.resource_model.appendRow([item, author, download_count, upload_date])

        if force_update:
            self.show_success_message("Successfully update the resources")

        self.resize_columns()
        self.update_title_bar()

    def update_filter_states(self):
        """
        Create a dictionary with resource types and their filter states.
        This method gets filter states from the tree selection.
        """
        selected_items = self.treeWidgetCategories.selectedItems()
        selected_types = None
        
        if selected_items:
            selected_types = selected_items[0].data(0, Qt.UserRole)
            
        # Default to all types selected if nothing is selected or "all" is selected
        is_all_selected = not selected_types or selected_types == "all"
        
        self.filter_states = {
            ResoureType.Geopackage: is_all_selected or (selected_types and ResoureType.Geopackage in selected_types),
            ResoureType.Style: is_all_selected or (selected_types and ResoureType.Style in selected_types),
            ResoureType.Model: is_all_selected or (selected_types and ResoureType.Model in selected_types),
            ResoureType.Model3D: is_all_selected or (selected_types and ResoureType.Model3D in selected_types),
            ResoureType.LayerDefinition: is_all_selected or (selected_types and ResoureType.LayerDefinition in selected_types),
        }

    def update_resource_filter(self):
        current_text = self.lineEditSearch.text()

        self.update_filter_states()

        filter_regexp_parts = ["NONE"]
        for resource_type, checked in self.filter_states.items():
            if checked:
                filter_regexp_parts.append(resource_type)

        filter_regexp = QRegExp("|".join(filter_regexp_parts), Qt.CaseInsensitive)
        self.proxy_model.setFilterRegExp(filter_regexp)
        self.proxy_model.setRolesToFilter([ResourceTypeRole])
        self.proxy_model.setCheckboxStates(self.filter_states)
        self.on_filter_text_changed(current_text)

    def on_filter_text_changed(self, text):
        self.proxy_model.setFilterRegExp(QRegExp(text, Qt.CaseInsensitive))
        self.proxy_model.setRolesToFilter([NameRole, CreatorRole])
        self.proxy_model.setCheckboxStates(self.filter_states)

        self.update_title_bar()

    @pyqtSlot("QItemSelection", "QItemSelection")
    def on_resource_selection_changed(self, selected, deselected):
        self.update_selected_resource()
        if self.selected_resource:
            self.update_preview()
            self.update_custom_button()
        else:
            self.log("No resource selected")

    def update_selected_resource(self):
        selected_indexes = []
        if self.viewStackedWidget.currentIndex() == 0:
            selected_indexes = self.listViewResources.selectionModel().selectedIndexes()
        elif self.viewStackedWidget.currentIndex() == 1:
            selected_indexes = self.treeViewResources.selectionModel().selectedIndexes()

        if len(selected_indexes) > 0:
            proxy_index = selected_indexes[0]
            source_index = self.proxy_model.mapToSource(proxy_index)
            self.selected_resource = self.resource_model.itemFromIndex(source_index)
        else:
            # Keep the previous selected in the attribute
            pass

    def update_custom_button(self):
        self.addQGISPushButton.setVisible(True)
        if self.selected_resource.resource_type == ResoureType.Model:
            self.addQGISPushButton.setText(self.tr("Add Model to QGIS"))
            self.addQGISPushButton.setToolTip(self.tr("Add the model to QGIS directly"))
        elif self.selected_resource.resource_type == ResoureType.Style:
            self.addQGISPushButton.setText(self.tr("Add Style to QGIS"))
            self.addQGISPushButton.setToolTip(
                self.tr("Add the style to QGIS style database")
            )
        elif self.selected_resource.resource_type == ResoureType.Geopackage:
            self.addQGISPushButton.setText(self.tr("Add Geopackage to QGIS"))
            self.addQGISPushButton.setToolTip(
                self.tr("Download and load the layers to QGIS")
            )
        elif self.selected_resource.resource_type == ResoureType.LayerDefinition:
            self.addQGISPushButton.setText(self.tr("Add Layer to QGIS"))
            self.addQGISPushButton.setToolTip(
                self.tr("Load the layer definition to QGIS")
            )
        else:
            self.addQGISPushButton.setVisible(False)

    def update_preview(self):
        resource = self.selected_resource
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
        pretty_upload_date = resource.upload_date.strftime("%d %B %Y").lstrip("0")
        self.labelUploaded.setText(pretty_upload_date)
        self.textBrowserDescription.setHtml(resource.description)

    def hide_preview(self):
        self.groupBoxPreview.hide()

    def show_preview(self):
        self.groupBoxPreview.show()

    def download_resource(self):
        resource = self.selected_resource
        file_extension = os.path.splitext(resource.file)[1]

        # Read the stored download location
        download_location = self.plg_settings.get_value_from_key(
            "download_location", exp_type=str
        )

        default_path = os.path.join(download_location, os.path.basename(resource.file))

        # Set filter based on the extension
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

            try:
                download_file(resource.file, Path(file_path))
                self.show_success_message(f"Downloaded {resource.name} to {file_path}")
                if self.checkBoxOpenDirectory.isChecked():
                    QDesktopServices.openUrl(
                        QUrl.fromLocalFile(str(Path(file_path).parent))
                    )

                self.plg_settings.set_value_from_key(
                    "download_location", str(Path(file_path).parent)
                )
            except DownloadError as e:
                self.show_error_message(str(e))

    def add_resource_to_qgis(self):
        try:
            if self.selected_resource.resource_type == ResoureType.Model:
                self.add_model_to_qgis()
            elif self.selected_resource.resource_type == ResoureType.Style:
                self.add_style_to_qgis()
            elif self.selected_resource.resource_type == ResoureType.Geopackage:
                self.add_geopackage_to_qgis()
            elif self.selected_resource.resource_type == ResoureType.LayerDefinition:
                self.add_layer_definition_to_qgis()
        except DownloadError as e:
            self.show_error_message(str(e))

    @show_busy_cursor
    def add_model_to_qgis(self):
        resource = self.selected_resource
        qgis_user_dir = QgsApplication.qgisSettingsDirPath()

        # Automatically download to qgis_hub subdirectory
        custom_model_directory = Path(qgis_user_dir, "processing", "models", "qgis_hub")
        if not custom_model_directory.exists():
            custom_model_directory.mkdir(parents=True, exist_ok=True)

        file_path = custom_model_directory / os.path.basename(resource.file)

        download_file(resource.file, file_path)
        # Refreshing the processing toolbox
        QgsApplication.processingRegistry().providerById("model").refreshAlgorithms()
        self.show_success_message(self.tr(f"Model {resource.name} is added to QGIS"))

    @show_busy_cursor
    def add_geopackage_to_qgis(self):
        resource = self.selected_resource
        file_extension = os.path.splitext(resource.file)[1]
        file_filter = self.tr("All files (*)")
        if file_extension == ".gpkg":
            file_filter = self.tr("Geopackage (*.gpkg)") + ";;" + file_filter
        elif file_extension == ".zip":
            file_filter = self.tr("ZIP Files (*.zip)") + ";;" + file_filter

        file_path = QFileDialog.getSaveFileName(
            self,
            self.tr("Save Resource"),
            resource.file,
            file_filter,
        )[0]

        if file_path:
            if not file_path.endswith(file_extension):
                file_path = file_path + file_extension

            download_file(resource.file, file_path)

        extract_location = Path(os.path.dirname(file_path))
        current_project = QgsProject.instance()

        if file_path.endswith(".zip"):
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(str(extract_location))
                extracted_folder_name = os.path.splitext(os.path.basename(file_path))[0]
                extracted_folder_path = extract_location / extracted_folder_name

            shapefiles = list(extracted_folder_path.glob("**/*.shp"))
            gpkg_files = list(extracted_folder_path.glob("**/*.gpkg"))

            for shapefile_path in shapefiles:
                layer_name = shapefile_path.stem
                layer = QgsVectorLayer(str(shapefile_path), layer_name, "ogr")

                if layer.isValid():
                    current_project.addMapLayer(layer)
                else:
                    self.show_warning_message(self.tr(f"Invalid layer: {layer_name}"))

            for gpkg_file in gpkg_files:
                layer_name = gpkg_file.stem
                self.load_geopackage(
                    current_project,
                    layer_name,
                    str(gpkg_file.absolute()),
                    resource_name=resource.name,
                )

        elif file_path.endswith(".gpkg"):
            self.load_geopackage(
                current_project,
                os.path.basename(file_path),
                file_path,
                resource_name=resource.name,
            )
        else:
            self.show_error_message(
                self.tr(
                    "Only Geopackage and zip file are supported. File is {file_path}".format(
                        file_path=file_path
                    )
                )
            )

    def load_geopackage(
        self, project, layer_name, gpkg_file_path, resource_name: str = ""
    ):
        geopackage = QgsVectorLayer(gpkg_file_path, layer_name, "ogr")
        if not resource_name:
            resource_name = os.path.basename(gpkg_file_path)
        if geopackage.isValid():
            # Add all layers from the geopackage to the project
            layers = geopackage.dataProvider().subLayers()
            valid_layer_num = 0
            for layer in layers:
                layer_parts = layer.split("!!::!!")
                layer_name = layer_parts[1]
                layer_uri = f"{gpkg_file_path}|layername={layer_name}"
                vector_layer = QgsVectorLayer(layer_uri, layer_name, "ogr")
                if vector_layer.isValid():
                    project.addMapLayer(vector_layer)
                    valid_layer_num += 1
                else:
                    self.show_warning_message(self.tr(f"Invalid layer: {layer_name}"))
            message = self.tr(
                f"Successfully load {valid_layer_num} of {len(layers)} layers from {resource_name}"
            )
            self.show_success_message(message)
        else:
            self.show_warning_message(self.tr(f"Invalid geopackage: {gpkg_file_path}"))

    @show_busy_cursor
    def add_style_to_qgis(self):
        resource = self.selected_resource
        tempdir = Path(
            "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()
        )
        tempfile_path = Path(tempdir, resource.file.split("/")[-1])
        download_file(resource.file, tempfile_path, True)

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

    @show_busy_cursor
    def add_layer_definition_to_qgis(self):
        resource = self.selected_resource

        layer_definition_dir = QGIS_HUB_DIR / "layer_definitions"
        file_path = layer_definition_dir / f"{resource.name}.qlr"

        if not layer_definition_dir.exists():
            layer_definition_dir.mkdir(parents=True, exist_ok=True)

        download_file(resource.file, file_path)

        current_project = QgsProject.instance()

        self.load_layer_definition(current_project, resource.name, file_path)

    def load_layer_definition(self, project, layer_name, layer_definition_file_path):
        success, message = QgsLayerDefinition.loadLayerDefinition(
            str(layer_definition_file_path), project, project.layerTreeRoot()
        )
        if success:
            self.show_success_message(
                self.tr(f"Successfully load layer definition: {layer_name}")
            )
        else:
            self.show_error_message(
                self.tr(f"Failed to load layer definition: {layer_name}: {message}")
            )

    def update_title_bar(self):
        num_total_resources = len(self.resources)
        num_selected_resources = self.proxy_model.rowCount()
        window_title = self.tr(
            f"QGIS Hub Explorer ({num_selected_resources} of {num_total_resources})"
        )
        self.setWindowTitle(window_title)

    def show_list_view(self):
        # Update the selected on other view
        selected_indexes = self.treeViewResources.selectionModel().selectedIndexes()
        if selected_indexes:
            self.listViewResources.selectionModel().select(
                selected_indexes[0], QItemSelectionModel.ClearAndSelect
            )
            self.listViewResources.setCurrentIndex(selected_indexes[0])

        # Show the list view
        self.viewStackedWidget.setCurrentIndex(1)

    def show_icon_view(self):
        # Update the selected on other view
        selected_indexes = self.listViewResources.selectionModel().selectedIndexes()
        if selected_indexes:
            self.treeViewResources.selectionModel().select(
                selected_indexes[0], QItemSelectionModel.ClearAndSelect
            )
            self.treeViewResources.setCurrentIndex(selected_indexes[0])

        # Show the icon (grid) view
        self.viewStackedWidget.setCurrentIndex(0)

    def resize_columns(self):
        if self.resource_model.rowCount() > 0:
            for i in range(self.resource_model.columnCount()):
                self.treeViewResources.resizeColumnToContents(i)

    def update_icon_size(self, size):
        self.listViewResources.setIconSize(QSize(size, size))

    def setup_resource_type_tree(self):
        """
        Setup the resource type tree widget with available resource types.
        The tree will have a main "Resource Types" item with child items for each resource type.
        """
        # Clear the tree widget
        self.treeWidgetCategories.clear()
        
        # Set up the header
        self.treeWidgetCategories.setHeaderLabel("Resource Types")
        
        # Create the root item
        self.treeWidgetCategories.invisibleRootItem()
        
        # Add resource type categories
        categories = {
            "Styles": [ResoureType.Style],
            "Geopackages": [ResoureType.Geopackage],
            "Models": [ResoureType.Model],
            "3D Models": [ResoureType.Model3D],
            "Layer Definitions": [ResoureType.LayerDefinition]
        }
        
        self.tree_items = {}
        
        # Add the "All Types" root item
        all_types_item = QTreeWidgetItem(self.treeWidgetCategories, ["All Types"])
        all_types_item.setData(0, Qt.UserRole, "all")
        all_types_item.setExpanded(True)
        
        # Add categories as children
        for category_name, types in categories.items():
            category_item = QTreeWidgetItem(all_types_item, [category_name])
            category_item.setData(0, Qt.UserRole, types)
            self.tree_items[category_name] = category_item
        
        # Connect the selection changed signal
        self.treeWidgetCategories.itemSelectionChanged.connect(self.on_tree_selection_changed)
        
        # Select the "All Types" item by default
        self.treeWidgetCategories.setCurrentItem(all_types_item)

    def on_tree_selection_changed(self):
        """
        Handle the selection change in the tree widget.
        Update the resource filter accordingly.
        """
        # Update the checkbox states dictionary (which is now just for filtering logic)
        self.update_filter_states()
        
        # Update the resource filter based on tree selection
        self.update_resource_filter()
