"""Tests for the mongodb adaptor"""
import unittest
import unittest.mock
from context import mongo_adaptor
import pymongo


class TestMongoCheckMalware(unittest.TestCase):
    """Check malware exists"""

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_malware_exists(self):
        """Check returns True when record exists"""
        self.assertFalse(True)


if __name__ == "__main__":
    unittest.main()
