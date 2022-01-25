"""mongo adaptor for url malware lookup database"""
from urlchecker.database_abc import DatabaseABC, DatabaseAbcT
import typing
from pymongo import MongoClient

import logging

logger = logging.getLogger(__name__)

MongoAdaptorT = typing.TypeVar("MongoAdaptorT", bound="MongoAdaptor")


class MongoAdaptor(DatabaseABC):
    """Concrete implementation of DatabaseABC using MongoDB as a backing store.

    :param conn: connection string to mongodb instance (e.g. "mongodb://localhost:27017/")
    :param username: mongodb username
    :param password: mongodb password
    :param str database: mongodb database
    :param str collection: mongodb collection
    """

    def __init__(
        self,
        username,
        password,
        database,
        collection,
        connection_string="mongodb://localhost:27017/",
    ) -> None:
        self.mongo_client = MongoClient(
            connection_string,
            username=username,
            password=password,
            authSource="admin",
            authMechanism="SCRAM-SHA-256",
        )
        self.collection = self.mongo_client[database][collection]
        # TODO: Is there a way to configure self.mongo_client.options.server_selection_timeout ? prop has no setter

    @classmethod
    def configure_from_dict(cls, options: dict) -> MongoAdaptorT:
        """Alternative constructor using options from from a configuration dictionary

        :param options: The configuration dictionary of the form specified in the documentation for this database adaptor with the exception of username and password. For this dict, username and password should contain the actual username and password rather than the names of the environment variables where they are stored.
        :type options: dict, required
        :return: A concrete subclass of DatabaseABC
        :rtype: DatabaseABC
        """
        try:
            connection_string = options["connection_string"]
            username = options["username"]
            password = options["password"]
            database = options["database"]
            collection = options["collection"]
        except KeyError as e:
            logger.error("Could not parse arguments from config dict", exc_info=e)
            raise ValueError("Could not parse options from dict. ")
        return cls(username, password, database, collection, connection_string)

    def check_url_has_malware(self, host_and_query: str) -> typing.Tuple[str, str]:
        """Checks if host_and_query is known to have malware

        Overrides DatabaseABC.check_url_has_malware
        """
        raise NotImplemented

    def check_any_url_has_malware(
        self, urls: typing.Iterable[str]
    ) -> typing.Tuple[str, str]:
        """Checks if any url in urls is known to have malware

        Overrides DatabaseABC.check_any_url_has_malware
        """
        cursor = self.collection.find({"url": {"$in": urls}})
        try:
            return ("unsafe", str(cursor[0]["reason"]))
        except IndexError:
            return ("safe", "")
