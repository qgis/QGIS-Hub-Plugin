from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtWidgets import QApplication


def show_busy_cursor(func):
    def wrapper(*args, **kwargs):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QCoreApplication.processEvents()

        try:
            return func(*args, **kwargs)
        finally:
            QApplication.restoreOverrideCursor()
            QCoreApplication.processEvents()

    return wrapper
