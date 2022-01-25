"""Tests for the mongodb adaptor"""
import unittest
import unittest.mock
from context import mongo_adaptor
from urlchecker.database_abc import DatabaseABC
from urlchecker.mongo_adaptor import MongoAdaptor


class TestMongoConfig(unittest.TestCase):
    """Test mongo constructors"""

    def test_mongo_constructor(self):
        mongo_client_adaptor = mongo_adaptor.MongoAdaptor.configure_from_dict(
            {
                "connection_string": "mongodb://localhost:27017/",
                "username": "root",
                "password": "example",
                "database": "urlinfo_sample",
                "collection": "urlinfo_sample",
            }
        )
        self.assertTrue(isinstance(mongo_client_adaptor, DatabaseABC))
        self.assertTrue(isinstance(mongo_client_adaptor, MongoAdaptor))


class TestMongoCheckMalware(unittest.TestCase):
    """Check malware exists"""

    def test_malware_exists(self):
        """Check returns True when record exists"""
        # self.assertFalse(True)
        pass  # TODO (needs to be mocked)


if __name__ == "__main__":
    unittest.main()
