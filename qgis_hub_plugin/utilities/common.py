import os
from pathlib import Path

from qgis.PyQt.QtGui import QIcon

from qgis_hub_plugin.__about__ import DIR_PLUGIN_ROOT
from qgis_hub_plugin.utilities.file_downloader import FileDownloader


def get_icon(icon_name: str):
    full_path = os.path.join(DIR_PLUGIN_ROOT, "resources", "images", icon_name)
    return QIcon(full_path)


def download_file(url: str, file_path: Path, force: bool = False):
    if not force and file_path.exists():
        return
    downloader = FileDownloader(url, str(file_path.absolute()))
    try:
        result, message = downloader.download()
    except OSError as ex:
        raise OSError(ex)

    return file_path.exists()
