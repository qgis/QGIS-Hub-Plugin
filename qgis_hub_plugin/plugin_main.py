#! python3  # noqa: E265

"""
Main plugin module.
"""

# standard
from functools import partial
from pathlib import Path

# PyQGIS
from qgis.core import QgsApplication, QgsSettings
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QCoreApplication, QLocale, QTranslator, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QAction

# project
from qgis_hub_plugin.__about__ import (
    DIR_PLUGIN_ROOT,
    __icon_path__,
    __title__,
    __uri_homepage__,
)
from qgis_hub_plugin.gui.dlg_settings import PlgOptionsFactory
from qgis_hub_plugin.gui.resource_browser import ResourceBrowserDialog
from qgis_hub_plugin.toolbelt import PlgLogger
from qgis_hub_plugin.utilities.common import get_icon

# ############################################################################
# ########## Classes ###############
# ##################################


class QgisHubPluginPlugin:
    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class which \
        provides the hook by which you can manipulate the QGIS application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.log = PlgLogger().log

        # translation
        # initialize the locale
        self.locale: str = QgsSettings().value("locale/userLocale", QLocale().name())[
            0:2
        ]
        locale_path: Path = (
            DIR_PLUGIN_ROOT / f"resources/i18n/{__title__.lower()}_{self.locale}.qm"
        )
        self.log(message=f"Translation: {self.locale}, {locale_path}", log_level=4)
        if locale_path.exists():
            self.translator = QTranslator()
            self.translator.load(str(locale_path.resolve()))
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        """Set up plugin UI elements."""

        # settings page within the QGIS preferences menu
        self.options_factory = PlgOptionsFactory()
        self.iface.registerOptionsWidgetFactory(self.options_factory)

        # Toolbar
        self.toolbar = self.iface.addToolBar("QGIS Hub Plugin")
        self.toolbar.setObjectName("QGIS Hub PluginToolbar")

        # -- Actions
        self.action_resource_browser = QAction(
            get_icon("QGIS_Hub_icon.svg"),
            self.tr("Open Resource Browser"),
            self.iface.mainWindow(),
        )
        self.action_resource_browser.triggered.connect(
            self._open_resource_browser_dialog
        )

        self.action_help = QAction(
            QgsApplication.getThemeIcon("mActionHelpContents.svg"),
            self.tr("Help"),
            self.iface.mainWindow(),
        )
        self.action_help.triggered.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
        )

        self.action_settings = QAction(
            QgsApplication.getThemeIcon("console/iconSettingsConsole.svg"),
            self.tr("Settings"),
            self.iface.mainWindow(),
        )
        self.action_settings.triggered.connect(
            lambda: self.iface.showOptionsDialog(currentPage=f"mOptionsPage{__title__}")
        )

        # -- Menu
        self.iface.addPluginToMenu(__title__, self.action_resource_browser)
        self.iface.addPluginToMenu(__title__, self.action_settings)
        self.iface.addPluginToMenu(__title__, self.action_help)

        # Toolbar
        self.toolbar.addAction(self.action_resource_browser)

        # -- Help menu

        # documentation
        self.iface.pluginHelpMenu().addSeparator()
        self.action_help_plugin_menu_documentation = QAction(
            QIcon(str(__icon_path__)),
            f"{__title__} - Documentation",
            self.iface.mainWindow(),
        )
        self.action_help_plugin_menu_documentation.triggered.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
        )

        self.iface.pluginHelpMenu().addAction(
            self.action_help_plugin_menu_documentation
        )

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def unload(self):
        """Cleans up when plugin is disabled/uninstalled."""
        # -- Clean up menu
        self.iface.removePluginMenu(__title__, self.action_help)
        self.iface.removePluginMenu(__title__, self.action_settings)
        self.iface.removePluginMenu(__title__, self.action_resource_browser)

        self.iface.removeToolBarIcon(self.action_resource_browser)
        self.iface.mainWindow().removeToolBar(self.toolbar)
        del self.toolbar

        # -- Clean up preferences panel in QGIS settings
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)

        # remove actions
        del self.action_settings
        del self.action_help
        del self.action_resource_browser

    def run(self):
        """Main process.

        :raises Exception: if there is no item in the feed
        """
        try:
            self.log(
                message=self.tr("Everything ran OK."),
                log_level=3,
                push=False,
            )
        except Exception as err:
            self.log(
                message=self.tr(f"Houston, we've got a problem: {err}"),
                log_level=2,
                push=True,
            )

    def _open_resource_browser_dialog(self):
        self.log("_open_resource_browser_dialog")
        dialog = ResourceBrowserDialog(
            self.iface.mainWindow(),
            self.iface,
        )
        dialog.show()
