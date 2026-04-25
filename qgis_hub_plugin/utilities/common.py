import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from qgis.core import QgsApplication, QgsNetworkAccessManager, QgsNetworkReplyContent
from qgis.PyQt.QtCore import QFile, QIODevice, QUrl
from qgis.PyQt.QtGui import QIcon, QImageReader
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest

from qgis_hub_plugin.__about__ import DIR_PLUGIN_ROOT
from qgis_hub_plugin.toolbelt import PlgLogger
from qgis_hub_plugin.utilities.exception import DownloadError

QGIS_HUB_DIR = Path(QgsApplication.qgisSettingsDirPath(), "qgis_hub")

# Image formats Qt can decode in this QGIS install (e.g. {"jpg", "png", "webp"}).
# Qt5 ships the webp plugin; Qt6 may not. Computed once at import time so we
# don't probe every thumbnail file on disk.
_QT_SUPPORTED_IMAGE_FORMATS = {
    bytes(fmt).decode("ascii").lower() for fmt in QImageReader.supportedImageFormats()
}


def _qt_can_decode(extension: str) -> bool:
    ext = extension.lower().lstrip(".")
    if ext == "jpg":
        ext = "jpeg"
    return ext in _QT_SUPPORTED_IMAGE_FORMATS or (
        ext == "jpeg" and "jpg" in _QT_SUPPORTED_IMAGE_FORMATS
    )


def normalize_resource_subtypes(resource_data: dict) -> list[str]:
    """
    Normalize resource subtypes from API response to a list format.

    Handles both old API format (resource_subtype: string) and new API format
    (resource_subtypes: array). Always returns a list of subtypes.

    Args:
        resource_data (dict): Resource data from API containing either
            'resource_subtypes' (new format) or 'resource_subtype' (old format)

    Returns:
        List[str]: List of subtypes. Empty list if no subtypes are present.

    Examples:
        >>> normalize_resource_subtypes({"resource_subtypes": ["symbol", "colorramp"]})
        ["symbol", "colorramp"]
        >>> normalize_resource_subtypes({"resource_subtype": "symbol"})
        ["symbol"]
        >>> normalize_resource_subtypes({"resource_subtype": ""})
        []
    """
    # Handle new API format (resource_subtypes array)
    if "resource_subtypes" in resource_data:
        subtypes = resource_data.get("resource_subtypes", [])
        # Ensure it's a list
        if isinstance(subtypes, list):
            return subtypes
        # Handle edge case where it might be a single value
        return [subtypes] if subtypes else []

    # Handle old API format (resource_subtype string)
    subtype = resource_data.get("resource_subtype", "")
    return [subtype] if subtype else []


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
        if reply.error() == QNetworkReply.NetworkError.NoError:
            file = QFile(str(destination))
            if file.open(QIODevice.OpenModeFlag.WriteOnly):
                file.write(reply.readAll())
                file.close()
                return destination
            else:
                raise DownloadError(
                    f"Failed to open file for writing: {file.errorString()}"
                )
        elif reply.error() == QNetworkReply.NetworkError.ContentNotFoundError:
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


def clear_cache() -> tuple[bool, int]:
    """Delete the cached API response and all cached thumbnails.

    Returns:
        Tuple[bool, int]: (response_file_removed, number_of_thumbnails_removed).
    """
    response_removed = False
    response_file = Path(QGIS_HUB_DIR, "response.json")
    if response_file.exists():
        response_file.unlink()
        response_removed = True

    thumbnails_removed = 0
    thumbnail_dir = Path(QGIS_HUB_DIR, "thumbnails")
    if thumbnail_dir.exists():
        thumbnails_removed = sum(1 for _ in thumbnail_dir.iterdir() if _.is_file())
        shutil.rmtree(thumbnail_dir)

    return response_removed, thumbnails_removed


def resource_thumbnail_cache_path(url: str, uuid: str) -> Optional[Path]:
    """Return the expected on-disk cache path for a resource thumbnail, or
    None if the resource has no downloadable thumbnail (missing URL or the
    default QGIS Hub icon)."""
    if not url or url.endswith("qgis-icon-32x32.png"):
        return None
    extension = "jpg"
    try:
        extension = url.split(".")[-1]
    except IndexError:
        pass
    return Path(QGIS_HUB_DIR, "thumbnails", f"{uuid}.{extension}")


def is_resource_thumbnail_cached(url: str, uuid: str) -> bool:
    path = resource_thumbnail_cache_path(url, uuid)
    return path is not None and path.exists()


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
    if not (status and thumbnail_path.exists()):
        return Path(get_icon_path("QGIS_Hub_icon.svg"))

    # Qt5 ships the webp image-format plugin, so this branch was a no-op
    # in QGIS 3. Qt6 in QGIS 4 may lack it: when Qt cannot decode this
    # extension, fall back to a one-shot Pillow conversion to PNG. The
    # PNG sibling is reused on subsequent calls so we never re-decode.
    if _qt_can_decode(extension):
        return thumbnail_path

    png_path = thumbnail_path.with_suffix(".png")
    if png_path.exists() and png_path.stat().st_size > 0:
        return png_path

    converted = _convert_thumbnail_to_png(thumbnail_path, png_path)
    if converted is not None:
        return converted
    return Path(get_icon_path("QGIS_Hub_icon.svg"))


def _convert_thumbnail_to_png(source: Path, target: Path) -> Optional[Path]:
    try:
        from PIL import Image
    except ImportError:
        PlgLogger.log(
            f"Cannot decode {source.name} and Pillow is unavailable for conversion."
        )
        return None
    try:
        with Image.open(source) as img:
            # Cap to a sensible thumbnail size so conversion stays fast even
            # when the source is a full-resolution screenshot/map preview.
            img.thumbnail((512, 512))
            img.convert("RGBA").save(target, format="PNG", optimize=True)
        return target
    except Exception as exc:  # noqa: BLE001
        PlgLogger.log(f"Failed to convert thumbnail {source.name}: {exc}")
        return None
