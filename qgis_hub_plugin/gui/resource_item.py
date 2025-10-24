from datetime import datetime

from qgis.PyQt.QtGui import QIcon, QStandardItem

from qgis_hub_plugin.gui.constants import (
    CreatorRole,
    NameRole,
    ResourceSubtypeRole,
    ResourceTypeRole,
    SortingRole,
)
from qgis_hub_plugin.utilities.common import download_resource_thumbnail, get_icon


class ResourceItem(QStandardItem):
    def __init__(self, params: dict):
        super().__init__()

        # Attribute from the QGIS Hub
        self.resource_type = params.get("resource_type")
        self.resource_subtype = params.get("resource_subtype", "")
        self.uuid = params.get("uuid")
        self.name = params.get("name").strip()
        self.creator = params.get("creator").strip()
        upload_date_string = params.get("upload_date")
        # Replace 'Z' with '+00:00' for Python < 3.11 compatibility
        if upload_date_string.endswith("Z"):
            upload_date_string = upload_date_string[:-1] + "+00:00"
        self.upload_date = datetime.fromisoformat(upload_date_string)
        self.download_count = params.get("download_count")
        self.description = params.get("description")
        self.dependencies = params.get("dependencies")  # Add support for dependencies
        self.file = params.get("file")
        self.thumbnail = params.get("thumbnail")

        # Custom attribute
        self.setText(self.name[:50] + "..." if len(self.name) > 50 else self.name)
        self.setToolTip(f"{self.name} by {self.creator}")
        thumbnail_path = download_resource_thumbnail(self.thumbnail, self.uuid)
        if thumbnail_path:
            self.setIcon(QIcon(str(thumbnail_path)))
        else:
            self.setIcon(get_icon("QGIS_Hub_icon.svg"))

        self.setData(self.resource_type, ResourceTypeRole)
        self.setData(self.name, NameRole)
        self.setData(self.creator, CreatorRole)
        self.setData(self.resource_subtype, ResourceSubtypeRole)


class AttributeSortingItem(QStandardItem):
    def __init__(self, display, value):
        super().__init__(display)
        self.setData(value, SortingRole)
