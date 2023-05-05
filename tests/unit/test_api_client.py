#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash
        # for whole tests
        python -m unittest tests.unit.test_plg_metadata
        # for specific test
        python -m unittest tests.unit.test_plg_metadata.TestPluginMetadata.test_version_semver
"""

# standard library
import unittest

# project
from qgis_hub_plugin.core.api_client import get_all_resources

# ############################################################################
# ########## Classes #############
# ################################


class TestApiClient(unittest.TestCase):

    """Test about module"""

    def test_get_all_resources(self):
        response = get_all_resources()
        self.assertIsNotNone(response)
        self.assertGreater(response.get("total"), 160)
        print(response.get("total"))
        # If this issue failed, we have to update the API limit
        self.assertIsNone(response.get("next"))


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
