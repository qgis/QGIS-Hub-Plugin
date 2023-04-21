import os
import shutil  # save img locally

import requests  # request img from web
from qgis.PyQt.QtGui import QIcon

from qgis_hub_plugin.__about__ import DIR_PLUGIN_ROOT


def get_icon(icon_name: str):
    full_path = os.path.join(DIR_PLUGIN_ROOT, "resources", "images", icon_name)
    return QIcon(full_path)


def download_image(url: str, file_path: str):
    response = requests.get(url, stream=True)
    with open(file_path, "wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

    # if response.status_code == 200:
    #     with open(file_path, "wb") as f:
    #         shutil.copyfileobj(response.raw, f)
    #         print("Image sucessfully Downloaded: ", file_path)
    # else:
    #     print("Image Couldn't be retrieved")
