"""Functions to translate a word or to get the locale."""
# Taken from https://github.com/inasafe/inasafe/blob/develop/safe/utilities/i18n.py


# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA pylint: disable=unused-import

# noinspection PyPackageRequirements
from qgis.PyQt.QtCore import QSettings  # QSettings can't be moved to our class
from qgis.PyQt.QtCore import QCoreApplication, QLocale

from qgis_hub_plugin.toolbelt import PlgLogger

log = PlgLogger.log


def tr(text, context="@default"):
    """We define a tr function alias here since the utilities implementation
    below is not a class and does not inherit from QObject.

    .. note:: see http://tinyurl.com/pyqt-differences

    :param text: String to be translated
    :type text: str, unicode

    :param context: A context for the translation. Since a same can be
        translated to different text depends on the context.
    :type context: str

    :returns: Translated version of the given string if available, otherwise
        the original string.
    :rtype: str, unicode
    """
    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    if type(text) != str:
        text = str(text)
    translated_text = QCoreApplication.translate(context, text)
    # Check if there is missing container. If so, return the original text.
    # See #3164
    if text.count("%") == translated_text.count("%"):
        return translated_text
    else:
        content = (
            "There is a problem in the translation text.\n"
            'The original text: "%s".\n'
            'The translation: "%s".\n'
            "The number of %% character does not match (%s and %s)."
            "Please check the translation in transifex for %s."
            % (
                text,
                translated_text,
                text.count("%"),
                translated_text.count("%s"),
                locale(),
            )
        )
        log(content)
        return text


def locale(qsetting=""):
    """Get the name of the currently active locale.

    :param qsetting: String to specify the QSettings. By default,
        use empty string.
    :type qsetting: str

    :returns: Name of the locale e.g. 'id'
    :rtype: str
    """
    override_flag = QSettings(qsetting).value("locale/overrideFlag", True, type=bool)

    default = "en_US"

    if override_flag:
        locale_name = QSettings(qsetting).value("locale/userLocale", default, type=str)
    else:
        # noinspection PyArgumentList
        locale_name = QLocale.system().name()

    if locale_name == "C":
        # On travis, locale/userLocale is equal to C. We want 'en'.
        locale_name = default

    # NOTES: we split the locale name because we need the first two
    # character i.e. 'id', 'af, etc
    locale_name = str(locale_name).split("_")[0]
    return locale_name
