import json
from pathlib import Path

from qgis.core import QgsApplication

from qgis_hub_plugin.utilities.common import download_file

BASE_URL = "https://hub.qgis.org/api/v1/resources/"


def get_all_resources(force_update=False):
    print("get_all_resources", force_update)
    # Check if the response file exits
    response_folder = Path(QgsApplication.qgisSettingsDirPath(), "qgis_hub")
    response_folder.mkdir(parents=True, exist_ok=True)
    response_file = Path(response_folder, "response.json")
    if not force_update and Path.exists(response_file):
        with open(response_file) as f:
            return json.load(f)

    # TODO: download in the background
    # hardcoded to get all resource, currently only ~227
    url = f"{BASE_URL}?limit=1000&format=json"
    status = download_file(url=url, destination=response_file, force=force_update)
    if status and response_file.exists():
        with open(response_file) as f:
            return json.load(f)
    else:
        return None
