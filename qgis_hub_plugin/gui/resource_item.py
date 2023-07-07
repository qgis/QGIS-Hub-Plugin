from datetime import datetime

from qgis.PyQt.QtGui import QIcon, QStandardItem

from qgis_hub_plugin.gui.constants import CreatorRole, NameRole, ResourceTypeRole
from qgis_hub_plugin.utilities.common import (
    download_resource_thumbnail,
    get_icon,
    shorten_string,
)


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
        self.upload_date = datetime.fromisoformat(upload_date_string)
        self.download_count = params.get("download_count")
        self.description = params.get("description")
        self.file = params.get("file")
        self.thumbnail = params.get("thumbnail")

        # Custom attribute
        self.setText(self.name)
        self.setToolTip(f"{self.name} by {self.creator}")
        thumbnail_path = download_resource_thumbnail(self.thumbnail, self.uuid)
        if thumbnail_path:
            self.setIcon(QIcon(str(thumbnail_path)))
        else:
            self.setIcon(get_icon("qbrowser_icon.svg"))

        self.setData(self.resource_type, ResourceTypeRole)
        self.setData(self.name, NameRole)
        self.setData(self.creator, CreatorRole)
