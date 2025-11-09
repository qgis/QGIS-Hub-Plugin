import json
from pathlib import Path

from qgis.core import QgsApplication

from qgis_hub_plugin.utilities.common import download_file
from qgis_hub_plugin.utilities.exception import DownloadError

BASE_URL = "https://hub.qgis.org/api/v1/resources/"
API_UNAVAILABLE_MESSAGE = (
    f"Unable to reach the QGIS Hub API. "
    f"Please check the QGIS Hub API status and try again. ({BASE_URL})"
)


def _load_response(response_file: Path):
    try:
        with open(response_file) as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise DownloadError(API_UNAVAILABLE_MESSAGE) from exc


def get_all_resources(force_update=False):
    # Check if the response file exits
    response_folder = Path(QgsApplication.qgisSettingsDirPath(), "qgis_hub")
    response_folder.mkdir(parents=True, exist_ok=True)
    response_file = Path(response_folder, "response.json")
    if not force_update and Path.exists(response_file):
        return _load_response(response_file)

    url = f"{BASE_URL}?limit=1000&format=json"
    try:
        status = download_file(url=url, destination=response_file, force=force_update)
    except DownloadError as exc:
        raise DownloadError(API_UNAVAILABLE_MESSAGE) from exc

    if status and response_file.exists():
        return _load_response(response_file)

    raise DownloadError(API_UNAVAILABLE_MESSAGE)
