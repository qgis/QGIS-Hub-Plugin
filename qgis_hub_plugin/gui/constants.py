from qgis.PyQt.QtCore import Qt

# Resource Item Data
ResourceTypeRole = Qt.UserRole + 1
NameRole = Qt.UserRole + 2
CreatorRole = Qt.UserRole + 3


class ResoureType:
    Model = "Model"
    Style = "Style"
    Geopackage = "Geopackage"
