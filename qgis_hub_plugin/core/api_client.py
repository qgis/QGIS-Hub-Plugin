# Quick implementation of api client to access QGIS Hub
import requests

BASE_URL = "https://plugins.qgis.org/api/v1/resources/"


def get_all_resources(params: dict = {}):
    params["format"] = "json"
    # params['limit'] = 50
    response = requests.get(BASE_URL, params=params)
    return response.json()
