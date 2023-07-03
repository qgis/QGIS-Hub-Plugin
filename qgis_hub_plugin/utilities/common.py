import os
from pathlib import Path

from qgis.core import QgsApplication, QgsSettings
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


def shorten_string(text: str) -> str:
    if len(text) > 20:
        text = text[:17] + "..."
    return text


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


def store_settings(setting_key, setting_value):
    settings = QgsSettings()
    settings.setValue("QGISResourceHubPlugin/" + setting_key, setting_value)


def read_settings(setting_key, default_value):
    settings = QgsSettings()
    stored_value = settings.value(
        "QGISResourceHubPlugin/" + setting_key, defaultValue=default_value
    )
    return stored_value
