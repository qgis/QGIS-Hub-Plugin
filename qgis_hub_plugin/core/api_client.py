# Quick implementation of api client to access QGIS Hub
import requests

BASE_URL = "https://plugins.qgis.org/api/v1/resources/"


def get_all_resources(params: dict = {}):
    params["format"] = "json"
    params["limit"] = 1000  # hardcoded to get all resource, currently only 160
    # TODO: download in the background
    response = requests.get(BASE_URL, params=params)
    return response.json()
