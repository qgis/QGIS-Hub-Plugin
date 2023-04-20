import os

from qgis.PyQt.QtGui import QIcon

from qgis_hub_plugin.__about__ import DIR_PLUGIN_ROOT


def get_icon(icon_name: str):
    full_path = os.path.join(DIR_PLUGIN_ROOT, "resources", "images", icon_name)
    return QIcon(full_path)
