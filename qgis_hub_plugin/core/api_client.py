import json
from pathlib import Path

import requests
from qgis.core import QgsApplication

BASE_URL = "https://plugins.qgis.org/api/v1/resources/"


def get_all_resources(params: dict = {}, force_update=False):
    params["format"] = "json"
    params["limit"] = 200  # hardcoded to get all resource, currently only 160

    # Check if the response file exits
    response_folder = Path(QgsApplication.qgisSettingsDirPath(), "qgis_hub")
    response_file = Path(response_folder, "response.json")
    if not force_update and Path.exists(response_file):
        with open(response_file) as f:
            return json.load(f)

    # TODO: download in the background
    response = requests.get(BASE_URL, params=params)

    # Store the response in a file
    response_folder.mkdir(parents=True, exist_ok=True)
    with open(response_file, "w") as f:
        json.dump(response.json(), f)

    return response.json()
