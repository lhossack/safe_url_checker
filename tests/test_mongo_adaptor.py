"""Tests for the mongodb adaptor"""
import unittest
import unittest.mock
from context import mongo_adaptor
from urlchecker.database_abc import DatabaseABC
from urlchecker.mongo_adaptor import MongoAdaptor
from urlchecker import mongo_adaptor
from pymongo import errors


class TestMongoConfig(unittest.TestCase):
    """Test mongo constructors"""

    def test_mongo_constructor(self):
        """Verify mongo constructor_from_dict returns a valid MongoAdaptor"""
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
    """Check cases where search returns/ does not return results"""

    def test_malware_url_exists(self):
        """Check adaptor responds correctly when a url in the input list is in the database"""
        mongo_client_adaptor = mongo_adaptor.MongoAdaptor.configure_from_dict(
            {
                "connection_string": "mongodb://localhost:27017/",
                "username": "root",
                "password": "example",
                "database": "urlinfo_sample",
                "collection": "urlinfo_sample",
            }
        )
        with unittest.mock.patch(
            "mongo_adaptor.pymongo.collection.Collection.find"
        ) as mock_find:

            class StubCursor:
                def __getitem__(self, index):
                    raise errors.InvalidOperation("Mock invalid operation")

            mock_find.return_value = StubCursor()
            mongo_client_adaptor.check_any_url_has_malware(
                ["good.com", "bad.com", "also-good.ca"]
            )

    def test_malware_not_exists(self):
        """Check adaptor responds correctly when no items match for any item in the list"""
        mongo_client_adaptor = mongo_adaptor.MongoAdaptor.configure_from_dict(
            {
                "connection_string": "mongodb://localhost:27017/",
                "username": "root",
                "password": "example",
                "database": "urlinfo_sample",
                "collection": "urlinfo_sample",
            }
        )
        with unittest.mock.patch(
            "mongo_adaptor.pymongo.collection.Collection.find"
        ) as mock_find:

            class StubCursor:
                def __getitem__(self, index):
                    return {"reason": "stubbed"}

            mock_find.return_value = StubCursor()
            ret = mongo_client_adaptor.check_any_url_has_malware(["bad.com"])
            self.assertEqual(ret[0], "unsafe")


if __name__ == "__main__":
    unittest.main()
