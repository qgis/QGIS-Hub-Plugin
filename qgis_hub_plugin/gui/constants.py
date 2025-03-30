from qgis.PyQt.QtCore import Qt

# Resource Item Data
ResourceTypeRole = Qt.UserRole + 1
NameRole = Qt.UserRole + 2
CreatorRole = Qt.UserRole + 3
SortingRole = Qt.UserRole + 4


# Type of resources, based on the QGIS Hub API
class ResoureType:
    Model = "Model"
    Style = "Style"
    Geopackage = "Geopackage"
    Model3D = "3DModel"
    LayerDefinition = "LayerDefinition"
    Map = "Map"
    Unknown = "Unknown"  # Catch-all for any new resource types added to the API in the future


# Resource type categories for display in the UI
ResoureTypeCategories = {
    "Styles": [ResoureType.Style],
    "Geopackages": [ResoureType.Geopackage],
    "Models": [ResoureType.Model],
    "3D Models": [ResoureType.Model3D],
    "Layer Definitions": [ResoureType.LayerDefinition],
    "Maps": [ResoureType.Map],
    "Other": [ResoureType.Unknown]  # Category for any unknown resource types
}
