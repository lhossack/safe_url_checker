"""Core business logic for checking databases of known malware"""
from .database_abc import DatabaseABC
import typing


class UrlChecker:
    """Main entry-point for checking URLs against databases of URLs known to contain malware.

    Registering a database adds the database to the list of databases checked for malware.

    :param typing.Iterable[DatabaseABC] databases: An iterable of concrete subclasses of DatabaseABC to register to the urlchecker
    :raises ValueError: In the case an invalid database adaptor is passed
    """

    def __init__(self, databases: typing.Iterable[DatabaseABC] = None) -> None:
        if not databases:
            self._databases = []
        else:
            for db in databases:
                self.register_database(db)

    def check_url_has_malware(self, host_and_query: str) -> bool:
        """Checks if URL is known to contain malware against all registered databases.

        Input query strings are of the form: "{hostname_and_port}/{original_path_and_query_string}".
        That is, they don't contain the protocol (e.g. "https://" is trimmed), but may include
        ports: e.g. https://www.google.com/search/path?query=1&here=2 should be passed in as
        www.google.com:443/search/path?query=1&here=2

        :param str host_and_query: Host and query
        :return: True if URL found to have malware in any database, False otherwise
        :rtype: bool
        """
        # TODO: Should an attempt be made to make urls be made uniform? (e.g. "evil.com" == "evil.com/"?)
        # TODO: Check hostname+port AND full url (make it easy to optionally block a full domain, or specific path)
        # TODO: Should urls be lowercased? (evil.com/malware_Page should be blocked if evil.com/malware_page is known)
        # TODO: Should urls be validated? (Do they need to be standards compliant?) -- assumption: only to extent needed to keep this service safe
        # TODO: parallelize calls to several dbs
        for db in self._databases:
            if db.check_url_has_malware(host_and_query):
                return True
        return False

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
