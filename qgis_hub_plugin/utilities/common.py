import os
import shutil  # save img locally
from pathlib import Path

import requests  # request img from web
from qgis.PyQt.QtGui import QIcon

from qgis_hub_plugin.__about__ import DIR_PLUGIN_ROOT


def get_icon(icon_name: str):
    full_path = os.path.join(DIR_PLUGIN_ROOT, "resources", "images", icon_name)
    return QIcon(full_path)


def download_file(url: str, file_path: Path, force: bool = False):
    # TODO: Use QgsNetworkManager here
    if force or not file_path.exists():
        response = requests.get(url, stream=True)
        with open(file_path.absolute(), "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

    return file_path.exists()
