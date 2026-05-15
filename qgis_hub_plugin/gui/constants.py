from qgis.PyQt.QtCore import Qt

# Resource Item Data
ResourceTypeRole = Qt.ItemDataRole.UserRole + 1
NameRole = Qt.ItemDataRole.UserRole + 2
CreatorRole = Qt.ItemDataRole.UserRole + 3
SortingRole = Qt.ItemDataRole.UserRole + 4
ResourceSubtypeRole = Qt.ItemDataRole.UserRole + 5


# Type of resources, based on the QGIS Hub API
# These are the known resource types, but the plugin will handle any new types dynamically
class ResoureType:
    Model = "Model"
    Style = "Style"
    Geopackage = "Geopackage"
    Model3D = "3DModel"
    LayerDefinition = "LayerDefinition"
    Map = "Map"
    ProcessingScripts = "ProcessingScript"
    Screenshot = "Screenshot"


# Resource type categories for display in the UI
# Any new resource type detected will be automatically added
ResoureTypeCategories = {
    "Styles": [ResoureType.Style],
    "Projects": [ResoureType.Geopackage],
    "Models": [ResoureType.Model],
    "3D Models": [ResoureType.Model3D],
    "QLR": [ResoureType.LayerDefinition],
    "Map Gallery": [ResoureType.Map],
    "Screenshots": [ResoureType.Screenshot],
    "Processing Scripts": [ResoureType.ProcessingScripts],
}
