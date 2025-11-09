#! python3  # noqa E265

"""
Unit tests for API client with mocked network calls.

This test module verifies the API client functionality without making
real network requests by mocking QgsApplication and network operations.

Usage from the repo root folder:

    .. code-block:: bash
        # for whole test module
        pytest tests/qgis/test_api_client_mocked.py -v
        # for specific test
        pytest tests/qgis/test_api_client_mocked.py::TestApiClientMocked::test_get_all_resources_with_cache -v
"""

import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from qgis_hub_plugin.utilities.exception import DownloadError


class TestApiClientMocked(unittest.TestCase):
    """Test API client with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_cache_dir = Path("/tmp/qgis_test/qgis_hub")
        self.mock_response_file = self.mock_cache_dir / "response.json"

    @patch("qgis_hub_plugin.core.api_client.QgsApplication")
    @patch("qgis_hub_plugin.core.api_client.download_file")
    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_get_all_resources_with_cache(
        self, mock_file, mock_exists, mock_download, mock_qgs_app
    ):
        """Test cache retrieval without network call."""
        from qgis_hub_plugin.core.api_client import get_all_resources

        # Setup mock paths
        mock_qgs_app.qgisSettingsDirPath.return_value = "/tmp/qgis_test"

        # Mock cached response exists
        mock_exists.return_value = True

        # Mock cached data
        mock_data = {
            "total": 5,
            "count": 5,
            "next": None,
            "results": [
                {
                    "uuid": "cached-uuid",
                    "name": "Cached Resource",
                    "resource_type": "model",
                }
            ],
        }
        mock_file.return_value.read.return_value = json.dumps(mock_data)
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(
            mock_data
        )

        # Call function without force update
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            result = get_all_resources(force_update=False)

        # Verify no download occurred
        mock_download.assert_not_called()

        # Verify cached data returned
        self.assertIsNotNone(result)
        self.assertEqual(result["total"], 5)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["uuid"], "cached-uuid")

    @patch("qgis_hub_plugin.core.api_client.QgsApplication")
    @patch("qgis_hub_plugin.core.api_client.download_file")
    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_get_all_resources_force_update(
        self, mock_file, mock_exists, mock_download, mock_qgs_app
    ):
        """Test forced API call bypasses cache."""
        from qgis_hub_plugin.core.api_client import get_all_resources

        # Setup mock paths
        mock_qgs_app.qgisSettingsDirPath.return_value = "/tmp/qgis_test"

        # Mock successful download
        mock_download.return_value = True
        mock_exists.return_value = True

        # Mock fresh API response
        mock_data = {
            "total": 10,
            "count": 10,
            "next": None,
            "results": [
                {
                    "uuid": "fresh-uuid",
                    "name": "Fresh Resource",
                    "resource_type": "style",
                }
            ],
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            result = get_all_resources(force_update=True)

        # Verify download was called with correct URL
        mock_download.assert_called_once()
        call_args = mock_download.call_args
        self.assertIn("limit=1000", call_args[1]["url"])
        self.assertIn("format=json", call_args[1]["url"])

        # Verify fresh data returned
        self.assertIsNotNone(result)
        self.assertEqual(result["total"], 10)

    @patch("qgis_hub_plugin.core.api_client.QgsApplication")
    @patch("qgis_hub_plugin.core.api_client.download_file")
    @patch("pathlib.Path.exists")
    def test_get_all_resources_download_failure(
        self, mock_exists, mock_download, mock_qgs_app
    ):
        """Test handling of download failures."""
        from qgis_hub_plugin.core.api_client import get_all_resources

        # Setup mock paths
        mock_qgs_app.qgisSettingsDirPath.return_value = "/tmp/qgis_test"

        # Mock download failure
        mock_download.return_value = False
        mock_exists.return_value = False

        # Call function with force update
        result = get_all_resources(force_update=True)

        # Verify None returned on failure
        self.assertIsNone(result)

    @patch("qgis_hub_plugin.core.api_client.QgsApplication")
    @patch("qgis_hub_plugin.core.api_client.download_file")
    @patch("pathlib.Path.exists")
    def test_get_all_resources_no_cache_first_run(
        self, mock_exists, mock_download, mock_qgs_app
    ):
        """Test first run when cache doesn't exist."""
        from qgis_hub_plugin.core.api_client import get_all_resources

        # Setup mock paths
        mock_qgs_app.qgisSettingsDirPath.return_value = "/tmp/qgis_test"

        # Mock cache doesn't exist
        mock_exists.return_value = False

        # Mock successful download but file still doesn't exist after
        mock_download.return_value = True

        result = get_all_resources(force_update=False)

        # Should attempt download when cache missing
        mock_download.assert_called_once()

    @patch("qgis_hub_plugin.core.api_client.QgsApplication")
    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_get_all_resources_json_parse_error(
        self, mock_file, mock_exists, mock_qgs_app
    ):
        """Test handling of corrupted cache file."""
        from qgis_hub_plugin.core.api_client import (
            API_UNAVAILABLE_MESSAGE,
            get_all_resources,
        )

        # Setup mock paths
        mock_qgs_app.qgisSettingsDirPath.return_value = "/tmp/qgis_test"
        mock_exists.return_value = True

        # Mock corrupted JSON
        mock_file.return_value.__enter__.return_value.read.return_value = (
            "{ invalid json"
        )

        # Should raise DownloadError with user-friendly message
        with self.assertRaises(DownloadError) as ctx:
            get_all_resources(force_update=False)
        self.assertEqual(str(ctx.exception), API_UNAVAILABLE_MESSAGE)

    @patch("qgis_hub_plugin.core.api_client.QgsApplication")
    @patch("qgis_hub_plugin.core.api_client.download_file")
    @patch("pathlib.Path.exists")
    def test_get_all_resources_download_error_user_message(
        self, mock_exists, mock_download, mock_qgs_app
    ):
        from qgis_hub_plugin.core.api_client import (
            API_UNAVAILABLE_MESSAGE,
            get_all_resources,
        )

        mock_qgs_app.qgisSettingsDirPath.return_value = "/tmp/qgis_test"
        mock_exists.return_value = False
        mock_download.side_effect = DownloadError("File not found (404 error)")

        with self.assertRaises(DownloadError) as ctx:
            get_all_resources(force_update=True)

        self.assertEqual(str(ctx.exception), API_UNAVAILABLE_MESSAGE)


@pytest.mark.parametrize(
    "force_update,cache_exists,expected_download_call",
    [
        (False, True, False),  # Use cache
        (False, False, True),  # No cache, download
        (True, True, True),  # Force update, download
        (True, False, True),  # Force update, download
    ],
)
def test_get_all_resources_parameterized(
    force_update, cache_exists, expected_download_call, mock_api_full_response
):
    """Test various combinations of force_update and cache states.

    Args:
        force_update: Whether to force update
        cache_exists: Whether cache file exists
        expected_download_call: Whether download should be called
        mock_api_full_response: Fixture providing mock API response
    """
    from qgis_hub_plugin.core.api_client import get_all_resources

    with patch("qgis_hub_plugin.core.api_client.QgsApplication") as mock_qgs:
        with patch("qgis_hub_plugin.core.api_client.download_file") as mock_download:
            with patch("pathlib.Path.exists") as mock_exists:
                # Setup
                mock_qgs.qgisSettingsDirPath.return_value = "/tmp/qgis_test"
                mock_exists.return_value = cache_exists
                mock_download.return_value = True

                # Mock file read
                with patch(
                    "builtins.open",
                    mock_open(read_data=json.dumps(mock_api_full_response)),
                ):
                    if cache_exists and not force_update:
                        result = get_all_resources(force_update=force_update)

                        # Verify
                        if expected_download_call:
                            mock_download.assert_called_once()
                        else:
                            mock_download.assert_not_called()

                        assert result is not None
                        assert result["total"] == 5


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
