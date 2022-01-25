"""mongo adaptor for url malware lookup database"""
from urlchecker.database_abc import DatabaseABC, DatabaseAbcT
import typing

import logging

logger = logging.getLogger(__name__)

MongoAdaptorT = typing.TypeVar("MongoAdaptorT", bound="MongoAdaptor")


class MongoAdaptor(DatabaseABC):
    """Manage mongo queries to a single database

    :param :
    """

    def __init__(self) -> None:
        pass

    @classmethod
    def configure_from_dict(cls, options: dict) -> MongoAdaptorT:
        """Alternative constructor using options from from a configuration dictionary

        :param options: The configuration dictionary of the form specified in the documentation for this database adaptor.
        :type options: dict, required
        :return: A concrete subclass of DatabaseABC
        :rtype: DatabaseABC
        """
        return cls()

    def check_url_has_malware(self, host_and_query: str) -> typing.Tuple[str, str]:
        """Check if url is associated with malware in this database.

        :param str host_and_query: Host and query string (e.g. "www.google.com/search/1/?q=search+term")
        :return (status, reason): ("unsafe", "reason") if URL found to have malware in this database, ("safe", "") or ("unknown", "") otherwise.
        :rtype: typing.Tuple[str, str]
        """
        return ("", "")
