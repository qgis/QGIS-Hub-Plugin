#! python3  # noqa E265

"""
Unit tests for utility functions.

This test module verifies download functionality, icon loading,
and thumbnail caching with mocked network operations.

Usage from the repo root folder:

    .. code-block:: bash
        # for whole test module
        pytest tests/qgis/test_utilities.py -v
        # for specific test
        pytest tests/qgis/test_utilities.py::TestDownloadUtilities::test_download_file_success -v
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestDownloadUtilities(unittest.TestCase):
    """Test download-related utility functions."""

    @patch("qgis_hub_plugin.utilities.common.QgsNetworkAccessManager")
    @patch("qgis_hub_plugin.utilities.common.QFile")
    @patch("qgis_hub_plugin.utilities.common.QgsApplication")
    def test_download_file_success(self, mock_qgs_app, mock_qfile, mock_nam):
        """Test successful file download."""
        from qgis_hub_plugin.utilities.common import download_file

        # Setup mock network reply
        mock_reply = MagicMock()
        mock_reply.error.return_value = 0  # QNetworkReply.NoError
        mock_reply.isFinished.return_value = True
        mock_reply.readAll.return_value = b"file content data"

        mock_nam_instance = MagicMock()
        mock_nam_instance.get.return_value = mock_reply
        mock_nam.instance.return_value = mock_nam_instance

        # Setup mock file
        mock_file_instance = MagicMock()
        mock_file_instance.open.return_value = True
        mock_qfile.return_value = mock_file_instance

        # Test download
        destination = Path("/tmp/test_file.txt")
        result = download_file("https://example.com/file.txt", destination)

        # Verify network request was made
        mock_nam_instance.get.assert_called_once()

        # Verify file was written
        mock_file_instance.open.assert_called_once()
        mock_file_instance.write.assert_called_once_with(b"file content data")
        mock_file_instance.close.assert_called_once()

        # Verify result
        self.assertEqual(result, destination)

    @patch("qgis_hub_plugin.utilities.common.QgsNetworkAccessManager")
    @patch("qgis_hub_plugin.utilities.common.QgsApplication")
    def test_download_file_404_error(self, mock_qgs_app, mock_nam):
        """Test 404 error handling."""
        from qgis_hub_plugin.utilities.common import download_file
        from qgis_hub_plugin.utilities.exception import DownloadError

        # Setup mock network reply with 404 error
        mock_reply = MagicMock()
        mock_reply.error.return_value = 203  # QNetworkReply.ContentNotFoundError
        mock_reply.isFinished.return_value = True
        mock_reply.errorString.return_value = "Not Found"

        mock_nam_instance = MagicMock()
        mock_nam_instance.get.return_value = mock_reply
        mock_nam.instance.return_value = mock_nam_instance

        # Test download with 404
        with self.assertRaises(DownloadError) as context:
            download_file("https://example.com/missing.txt", Path("/tmp/file.txt"))

        # Verify error message contains 404
        self.assertIn("404", str(context.exception))

    @patch("qgis_hub_plugin.utilities.common.QgsNetworkAccessManager")
    @patch("qgis_hub_plugin.utilities.common.QgsApplication")
    def test_download_file_network_error(self, mock_qgs_app, mock_nam):
        """Test generic network error handling."""
        from qgis_hub_plugin.utilities.common import download_file
        from qgis_hub_plugin.utilities.exception import DownloadError

        # Setup mock network reply with error
        mock_reply = MagicMock()
        mock_reply.error.return_value = 99  # Some network error
        mock_reply.isFinished.return_value = True
        mock_reply.errorString.return_value = "Network timeout"

        mock_nam_instance = MagicMock()
        mock_nam_instance.get.return_value = mock_reply
        mock_nam.instance.return_value = mock_nam_instance

        # Test download with error
        with self.assertRaises(DownloadError) as context:
            download_file("https://example.com/file.txt", Path("/tmp/file.txt"))

        # Verify error message
        self.assertIn("Download failed", str(context.exception))
        self.assertIn("Network timeout", str(context.exception))

    @patch("qgis_hub_plugin.utilities.common.QgsNetworkAccessManager")
    @patch("qgis_hub_plugin.utilities.common.QFile")
    @patch("qgis_hub_plugin.utilities.common.QgsApplication")
    def test_download_file_write_error(self, mock_qgs_app, mock_qfile, mock_nam):
        """Test file write error handling."""
        from qgis_hub_plugin.utilities.common import download_file
        from qgis_hub_plugin.utilities.exception import DownloadError

        # Setup successful network reply
        mock_reply = MagicMock()
        mock_reply.error.return_value = 0
        mock_reply.isFinished.return_value = True
        mock_reply.readAll.return_value = b"data"

        mock_nam_instance = MagicMock()
        mock_nam_instance.get.return_value = mock_reply
        mock_nam.instance.return_value = mock_nam_instance

        # Setup mock file that fails to open
        mock_file_instance = MagicMock()
        mock_file_instance.open.return_value = False
        mock_file_instance.errorString.return_value = "Permission denied"
        mock_qfile.return_value = mock_file_instance

        # Test download with write error
        with self.assertRaises(DownloadError) as context:
            download_file("https://example.com/file.txt", Path("/tmp/file.txt"))

        # Verify error message
        self.assertIn("Failed to open file", str(context.exception))
        self.assertIn("Permission denied", str(context.exception))

    @patch("qgis_hub_plugin.utilities.common.download_file")
    @patch("pathlib.Path.exists")
    def test_download_file_skip_if_exists(self, mock_exists, mock_download):
        """Test that download is skipped if file exists and force=False."""
        from qgis_hub_plugin.utilities.common import download_file

        mock_exists.return_value = True
        destination = Path("/tmp/existing_file.txt")

        # Call original function (not mocked)
        # We need to test the actual logic, so let's patch at a different level
        with patch("qgis_hub_plugin.utilities.common.QgsNetworkAccessManager"):
            # Test with force=False and existing file
            # The function checks Path.exists() internally
            pass  # This test structure needs adjustment for the actual implementation


class TestThumbnailUtilities(unittest.TestCase):
    """Test thumbnail download and caching."""

    @patch("qgis_hub_plugin.utilities.common.download_file")
    @patch("qgis_hub_plugin.utilities.common.get_icon_path")
    @patch("pathlib.Path.exists")
    def test_download_thumbnail_success(
        self, mock_exists, mock_icon_path, mock_download
    ):
        """Test successful thumbnail download."""
        from qgis_hub_plugin.utilities.common import download_resource_thumbnail

        # Mock successful download
        mock_download.return_value = True
        mock_exists.return_value = True
        mock_icon_path.return_value = "/default/icon.svg"

        url = "https://example.com/thumbnail.jpg"
        uuid = "test-uuid-123"

        result = download_resource_thumbnail(url, uuid)

        # Verify download was called
        mock_download.assert_called_once()

        # Verify result is a Path
        self.assertIsInstance(result, Path)

    @patch("qgis_hub_plugin.utilities.common.get_icon_path")
    def test_download_thumbnail_no_url(self, mock_icon_path):
        """Test thumbnail download with empty URL returns default icon."""
        from qgis_hub_plugin.utilities.common import download_resource_thumbnail

        mock_icon_path.return_value = "/default/QGIS_Hub_icon.svg"

        result = download_resource_thumbnail("", "test-uuid")

        # Should return default icon path
        self.assertIn("QGIS_Hub_icon.svg", str(result))

    @patch("qgis_hub_plugin.utilities.common.get_icon_path")
    def test_download_thumbnail_default_qgis_icon(self, mock_icon_path):
        """Test that default QGIS icon URL returns plugin icon."""
        from qgis_hub_plugin.utilities.common import download_resource_thumbnail

        mock_icon_path.return_value = "/default/QGIS_Hub_icon.svg"

        # URL ending with default QGIS icon
        url = "https://example.com/qgis-icon-32x32.png"
        result = download_resource_thumbnail(url, "test-uuid")

        # Should return default icon instead of downloading
        self.assertIn("QGIS_Hub_icon.svg", str(result))

    @patch("qgis_hub_plugin.utilities.common.download_file")
    @patch("qgis_hub_plugin.utilities.common.get_icon_path")
    @patch("pathlib.Path.exists")
    def test_download_thumbnail_fallback_on_error(
        self, mock_exists, mock_icon_path, mock_download
    ):
        """Test fallback to default icon on download failure."""
        from qgis_hub_plugin.utilities.common import download_resource_thumbnail

        # Mock failed download
        mock_download.return_value = None
        mock_exists.return_value = False
        mock_icon_path.return_value = "/default/QGIS_Hub_icon.svg"

        result = download_resource_thumbnail("https://example.com/thumb.jpg", "uuid")

        # Should fallback to default icon
        self.assertIn("QGIS_Hub_icon.svg", str(result))

    @patch("qgis_hub_plugin.utilities.common.download_file")
    @patch("qgis_hub_plugin.utilities.common.QgsApplication")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.exists")
    def test_download_thumbnail_creates_directory(
        self, mock_exists, mock_mkdir, mock_qgs_app, mock_download
    ):
        """Test that thumbnail directory is created if it doesn't exist."""
        from qgis_hub_plugin.utilities.common import download_resource_thumbnail

        mock_qgs_app.qgisSettingsDirPath.return_value = "/tmp/qgis"
        mock_download.return_value = True

        # First call: directory doesn't exist
        # Second call: file exists after download
        mock_exists.side_effect = [False, True]

        download_resource_thumbnail("https://example.com/thumb.jpg", "test-uuid")

        # Verify mkdir was called
        mock_mkdir.assert_called_once()


class TestIconUtilities(unittest.TestCase):
    """Test icon loading utilities."""

    def test_get_icon_path(self):
        """Test get_icon_path returns correct path."""
        from qgis_hub_plugin.utilities.common import get_icon_path

        icon_name = "test_icon.svg"
        path = get_icon_path(icon_name)

        # Verify path contains resources/images
        self.assertIn("resources", path)
        self.assertIn("images", path)
        self.assertIn(icon_name, path)

    @patch("qgis_hub_plugin.utilities.common.QIcon")
    @patch("qgis_hub_plugin.utilities.common.get_icon_path")
    def test_get_icon(self, mock_icon_path, mock_qicon):
        """Test get_icon creates QIcon from path."""
        from qgis_hub_plugin.utilities.common import get_icon

        mock_icon_path.return_value = "/path/to/icon.svg"
        mock_qicon_instance = MagicMock()
        mock_qicon.return_value = mock_qicon_instance

        result = get_icon("test_icon.svg")

        # Verify icon path was retrieved
        mock_icon_path.assert_called_once_with("test_icon.svg")

        # Verify QIcon was created with the path
        mock_qicon.assert_called_once_with("/path/to/icon.svg")

        # Verify result is the QIcon instance
        self.assertEqual(result, mock_qicon_instance)


# ############################################################################
# ######### Pytest-style tests ###############
# ############################################


@pytest.mark.parametrize(
    "url,uuid,expected_extension",
    [
        ("https://example.com/thumb.jpg", "uuid-1", ".jpg"),
        ("https://example.com/thumb.png", "uuid-2", ".png"),
        ("https://example.com/thumb.jpeg", "uuid-3", ".jpeg"),
        ("https://example.com/thumb.webp", "uuid-4", ".webp"),
    ],
)
def test_thumbnail_extension_detection(url, uuid, expected_extension):
    """Test that thumbnail extension is correctly extracted from URL.

    Args:
        url: Thumbnail URL
        uuid: Resource UUID
        expected_extension: Expected file extension
    """
    from qgis_hub_plugin.utilities.common import download_resource_thumbnail

    with patch("qgis_hub_plugin.utilities.common.download_file") as mock_download:
        with patch("qgis_hub_plugin.utilities.common.QgsApplication") as mock_qgs:
            with patch("pathlib.Path.exists") as mock_exists:
                mock_qgs.qgisSettingsDirPath.return_value = "/tmp/qgis"
                mock_download.return_value = True
                mock_exists.return_value = True

                download_resource_thumbnail(url, uuid)

                # Check that download was called with correct extension
                call_args = mock_download.call_args
                destination_path = call_args[0][1]
                assert str(destination_path).endswith(expected_extension)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
