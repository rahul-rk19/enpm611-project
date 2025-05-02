import unittest
import config
import os


class TestConfig(unittest.TestCase):

    def setUp(self):
        # Make sure the test_key environment variable doesn't interfere
        os.environ.pop("test_key", None)

    def test_set_and_get_parameter(self):
        # Test that set_parameter correctly stores a value, and get_parameter retrieves it
        config.set_parameter("test_key", "test_value")
        self.assertEqual(config.get_parameter("test_key"), "test_value")

    def test_get_parameter_missing_returns_none(self):
        # Test that get_parameter returns None if key hasn't been set
        self.assertIsNone(config.get_parameter("nonexistent_key"))


if __name__ == "__main__":
    unittest.main()

