from datetime import datetime

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon, QPainter, QPixmap, QStandardItem

from qgis_hub_plugin.gui.constants import (
    CreatorRole,
    NameRole,
    ResourceSubtypeRole,
    ResourceTypeRole,
    SortingRole,
)
from qgis_hub_plugin.utilities.common import (
    download_resource_thumbnail,
    get_icon,
    normalize_resource_subtypes,
)


class ResourceItem(QStandardItem):
    def __init__(self, params: dict):
        super().__init__()

        self.resource_type = params.get("resource_type")
        self.resource_subtypes = normalize_resource_subtypes(params)
        # First subtype kept for backward compatibility
        self.resource_subtype = (
            self.resource_subtypes[0] if self.resource_subtypes else ""
        )

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
        self.dependencies = params.get("dependencies")
        self.file = params.get("file")
        self.thumbnail = params.get("thumbnail")

        self.setText(self.name[:50] + "..." if len(self.name) > 50 else self.name)
        self.setToolTip(f"{self.name} by {self.creator}")
        thumbnail_path = download_resource_thumbnail(self.thumbnail, self.uuid)
        self.setIcon(self._make_uniform_icon(thumbnail_path))

        self.setData(self.resource_type, ResourceTypeRole)
        self.setData(self.name, NameRole)
        self.setData(self.creator, CreatorRole)
        self.setData(self.resource_subtypes, ResourceSubtypeRole)

    @staticmethod
    def _make_uniform_icon(thumbnail_path, target_size=512):
        """Return a square QIcon for *thumbnail_path*, centered on a transparent canvas.

        Normalises varying thumbnail aspect ratios so every cell in the
        QListView grid is the same size. Falls back to the default hub icon
        when the image cannot be loaded.
        """
        if not thumbnail_path or thumbnail_path.name == "QGIS_Hub_icon.svg":
            return get_icon("QGIS_Hub_icon.svg")

        pixmap = QPixmap(str(thumbnail_path))
        if pixmap.isNull():
            return get_icon("QGIS_Hub_icon.svg")

        # Scale to fit inside the target square, keeping aspect ratio
        scaled = pixmap.scaled(
            target_size,
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Paint centered on a transparent square canvas
        canvas = QPixmap(target_size, target_size)
        canvas.fill(Qt.GlobalColor.transparent)

        painter = QPainter(canvas)
        x = (target_size - scaled.width()) // 2
        y = (target_size - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)
        painter.end()

        return QIcon(canvas)


class AttributeSortingItem(QStandardItem):
    def __init__(self, display, value):
        super().__init__(display)
        self.setData(value, SortingRole)
