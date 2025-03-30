from qgis.PyQt.QtCore import Qt

# Resource Item Data
ResourceTypeRole = Qt.UserRole + 1
NameRole = Qt.UserRole + 2
CreatorRole = Qt.UserRole + 3
SortingRole = Qt.UserRole + 4


# Type of resources, based on the QGIS Hub API
# These are the known resource types, but the plugin will handle any new types dynamically
class ResoureType:
    Model = "Model"
    Style = "Style"
    Geopackage = "Geopackage"
    Model3D = "3DModel"
    LayerDefinition = "LayerDefinition"
    Map = "Map"


# Resource type categories for display in the UI
# Any new resource type detected will be automatically added
ResoureTypeCategories = {
    "Styles": [ResoureType.Style],
    "Geopackages": [ResoureType.Geopackage],
    "Models": [ResoureType.Model],
    "3D Models": [ResoureType.Model3D],
    "Layer Definitions": [ResoureType.LayerDefinition],
    "Maps": [ResoureType.Map],
}
