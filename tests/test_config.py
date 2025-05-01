import unittest
import config
import os


class TestConfig(unittest.TestCase):

    def setUp(self):
        # Clean up environment variables before each test
        os.environ.pop("test_key", None)

    def test_set_and_get_parameter(self):
        config.set_parameter("test_key", "test_value")
        self.assertEqual(config.get_parameter("test_key"), "test_value")

    def test_get_parameter_missing_returns_none(self):
        self.assertIsNone(config.get_parameter("nonexistent_key"))


if __name__ == "__main__":
    unittest.main()
