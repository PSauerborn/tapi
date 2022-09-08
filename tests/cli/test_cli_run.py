import unittest

from pydantic import ValidationError

from tapi.cli.run.command import (
    get_api_config,
    get_endpoint_handler,
    InvalidHandlerFunctionException,
)
from tapi.cli.run.models import APIConfig


class CLIUnittests(unittest.TestCase):
    """Unittest suite for the Tapi CLI"""

    def test_get_endpoint_handler(self):
        """Test function used to retrieve callable
        function from specified module"""

        try:
            get_endpoint_handler("tests.cli.files.sample.execute_addition")
        except Exception:
            self.fail()

        self.assertRaises(
            InvalidHandlerFunctionException,
            get_endpoint_handler,
            "tests.cli.files.sample.NOT_A_FUNCTION",
        )

    def test_get_api_config(self):
        """Test function used to generate API
        config from a provided YAML file"""

        cfg = get_api_config("tests/cli/files/sample.yml")
        self.assertIsInstance(cfg, APIConfig)

        self.assertRaises(
            ValidationError, get_api_config, "tests/cli/files/invalid-config.yml"
        )
