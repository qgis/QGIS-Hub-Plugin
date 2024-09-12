import os
from pathlib import Path
from typing import Optional

from qgis.core import QgsApplication, QgsNetworkAccessManager, QgsNetworkReplyContent
from qgis.PyQt.QtCore import QFile, QIODevice, QUrl
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest

from qgis_hub_plugin.__about__ import DIR_PLUGIN_ROOT
from qgis_hub_plugin.toolbelt import PlgLogger
from qgis_hub_plugin.utilities.exception import DownloadError

QGIS_HUB_DIR = Path(QgsApplication.qgisSettingsDirPath(), "qgis_hub")


def get_icon(icon_name: str) -> QIcon:
    full_path = get_icon_path(icon_name)
    return QIcon(full_path)


def get_icon_path(icon_name: str) -> str:
    return os.path.join(DIR_PLUGIN_ROOT, "resources", "images", icon_name)


def download_file(
    url: str, destination: Path, force: bool = True, timeout: int = 30000
) -> Optional[str]:
    """
    Download a file from the given URL to the specified destination using PyQGIS.

    Args:
        url (str): The URL of the file to download.
        destination (Path): The local path where the file should be saved.
        force (bool): If true, the file will be downloaded even if it already exists.
            Defaults to True.
        timeout (int): The timeout for the request in milliseconds. Defaults to 30000 (30 seconds).

    Returns:
        Optional[Path]: The path to the downloaded file if successful, None otherwise.

    Raises:
        DownloadError: If any error occurs during the download process.
    """
    if not force and destination.exists():
        return destination
    nam = QgsNetworkAccessManager.instance()
    request = QNetworkRequest(QUrl(url))
    request.setTransferTimeout(timeout)

    def handle_finished(reply: QgsNetworkReplyContent):
        if reply.error() == QNetworkReply.NoError:
            file = QFile(str(destination))
            if file.open(QIODevice.WriteOnly):
                file.write(reply.readAll())
                file.close()
                return destination
            else:
                raise DownloadError(
                    f"Failed to open file for writing: {file.errorString()}"
                )
        elif reply.error() == QNetworkReply.ContentNotFoundError:
            raise DownloadError(f"File not found (404 error): {url}")
        else:
            raise DownloadError(f"Download failed: {reply.errorString()}")

    try:
        reply = nam.get(request)

        # Use a loop to process events and prevent GUI freezing
        while not reply.isFinished():
            QgsApplication.processEvents()

        return handle_finished(reply)
    except Exception as e:
        if isinstance(e, DownloadError):
            raise e
        else:
            raise DownloadError(f"An unexpected error occurred: {str(e)}")


# If not able to download or not found, set the thumbnail to the default one
def download_resource_thumbnail(url: str, uuid: str) -> Path:
    if not url:
        PlgLogger.log(f"UUID: {uuid} has URL == None: {url}")
        return Path(get_icon_path("QGIS_Hub_icon.svg"))
    # If the URL is the default QGIS Hub icon, return the default icon.
    # Because it is not a thumbnail and it is too small
    if url.endswith("qgis-icon-32x32.png"):
        return Path(get_icon_path("QGIS_Hub_icon.svg"))

    # Assume it as jpg
    extension = ".jpg"
    try:
        extension = url.split(".")[-1]
    except IndexError as e:
        PlgLogger.log(f"UUID: {uuid} on URL: {url} get index error: {e}")

    thumbnail_dir = Path(QGIS_HUB_DIR, "thumbnails")
    thumbnail_path = Path(thumbnail_dir, f"{uuid}.{extension}")
    if not thumbnail_dir.exists():
        thumbnail_dir.mkdir(parents=True, exist_ok=True)

    status = download_file(url, thumbnail_path, False)
    if status and thumbnail_path.exists():
        return thumbnail_path
    else:
        return Path(get_icon_path("QGIS_Hub_icon.svg"))
