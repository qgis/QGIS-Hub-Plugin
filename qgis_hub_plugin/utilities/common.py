import os
from pathlib import Path

from qgis.core import QgsApplication
from qgis.PyQt.QtGui import QIcon

from qgis_hub_plugin.__about__ import DIR_PLUGIN_ROOT
from qgis_hub_plugin.toolbelt import PlgLogger
from qgis_hub_plugin.utilities.file_downloader import FileDownloader


def get_icon(icon_name: str) -> QIcon:
    full_path = get_icon_path(icon_name)
    return QIcon(full_path)


def get_icon_path(icon_name: str) -> str:
    return os.path.join(DIR_PLUGIN_ROOT, "resources", "images", icon_name)


def download_file(url: str, file_path: Path, force: bool = False):
    if not force and file_path.exists():
        return
    downloader = FileDownloader(url, str(file_path.absolute()))
    try:
        result, message = downloader.download()
    except OSError as ex:
        raise OSError(ex)

    return file_path.exists()


# If not able to download or not found, set the thumbnail to the default one
def download_resource_thumbnail(url: str, uuid: str) -> Path:
    if not url:
        PlgLogger.log(f"UUID: {uuid} has URL == None: {url}")
        return Path(get_icon_path("QGIS_Hub_icon.svg"))

    qgis_user_dir = QgsApplication.qgisSettingsDirPath()
    # Assume it as jpg
    extension = ".jpg"
    try:
        extension = url.split(".")[-1]
    except IndexError as e:
        PlgLogger.log(f"UUID: {uuid} on URL: {url} get index error: {e}")

    thumbnail_dir = Path(qgis_user_dir, "qgis_hub", "thumbnails")
    thumbnail_path = Path(thumbnail_dir, f"{uuid}.{extension}")
    if not thumbnail_dir.exists():
        thumbnail_dir.mkdir(parents=True, exist_ok=True)

    download_file(url, thumbnail_path)
    if thumbnail_path.exists():
        return thumbnail_path
    else:
        return Path(get_icon_path("QGIS_Hub_icon.svg"))
