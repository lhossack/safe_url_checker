"""Core business logic for checking databases of known malware"""
from .database_abc import DatabaseABC
import typing
import urllib.parse as parse

import logging

logger = logging.getLogger(__name__)


class UrlChecker:
    """Main entry-point for checking URLs against databases of URLs known to contain malware.

    Registering a database adds the database to the list of databases checked for malware.

    :param typing.Iterable[DatabaseABC] databases: An iterable of concrete subclasses of DatabaseABC to register to the urlchecker
    :raises ValueError: In the case an invalid database adaptor is passed
    """

    def __init__(self, databases: typing.Iterable[DatabaseABC] = None) -> None:
        self._databases = []
        if databases:
            for db in databases:
                self.register_database(db)

    def check_url_has_malware(self, host_and_query: str) -> typing.Tuple[str, str]:
        """Checks if URL is known to contain malware against all registered databases.

        Input query strings are of the form: "{hostname_and_port}/{original_path_and_query_string}".
        That is, they don't contain the protocol (e.g. "https://" is trimmed), but may include
        ports: e.g. https://www.google.com/search/path?query=1&here=2 should be passed in as
        www.google.com:443/search/path?query=1&here=2

        :param str host_and_query: Host and query
        :return (status, reason): status is "unsafe", "unknown" or "safe". Reason describes justification from tools populating the database.
        :rtype: typing.Tuple[str, str]
        """
        # TODO: potentialy parallelize calls to several dbs, current method will block on each access sequentially
        # TODO: ^ needs profiling under load conditions similar to production, this won't matter if process is or becomes cpu bound
        try:
            parsed_query = parse.urlparse("http://" + host_and_query)
        except ValueError:
            logger.info(f"Failed to parse {host_and_query}")
            return ("unsafe", "could not parse url")
        search_queries = [
            parsed_query.netloc,
            str(parsed_query.netloc) + parsed_query.path,
            str(parsed_query.netloc) + parsed_query.path + "?" + parsed_query.query,
        ]
        logger.debug(search_queries)
        for query in search_queries:
            for db in self._databases:
                result, reason = db.check_url_has_malware(query)
                if result == "unsafe":
                    return ("unsafe", reason)

        return ("safe", "")

    def register_database(self, database: DatabaseABC) -> None:
        """Register a database with the url checker.

        Registering a database adds the database to the list of databases checked for malware

        :param DatabaseABC database: A concrete subclass of DatabaseABC to register to the urlchecker
        :raises ValueError: In the case an invalid database adaptor is passed
        """
        if issubclass(type(database), DatabaseABC):
            self._databases.append(database)
        else:
            raise ValueError("Database is not an instance of DatabaseABC.")

    def get_db_count(self) -> int:
        """Get the number of databases registered to the UrlChecker

        :return: total number of databases registered
        :rtype: int
        """
        return len(self._databases)
