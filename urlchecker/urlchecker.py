from .databaseABC import DatabaseABC
import typing

class UrlChecker:
    """Manages checking URLs against databases of URLs known to contain malware.
    
    This is the main entry-point to the business logic for checking URLs
    """
    def __init__(self, databases: typing.Iterable[DatabaseABC] = None) -> None:
        """Initialize the UrlChecker, optionally with an iterable of databases

        Registering a database adds the database to the list of databases checked for malware
        :databases typing.Iterable[DatabaseABC]: An iterable of concrete subclasses of DatabaseABC to register to the urlchecker
        :raises ValueError: In the case an invalid database adaptor is passed
        """
        if not databases:
            self._databases = []
        else:
            for db in databases:
                self.register_database(db)

    def check_url_has_malware(self, host_and_query: str):
        """Checks if URL is known to contain malware against all registered databases.

        :param str host_and_query: Host and query in format: {hostname_and_port}/{original_path_and_query_string} That is, they don't contain the protocol (e.g. "https://" is trimmed), but may include ports: e.g. https://www.google.com/search/path?query=1&here=2 should be passed in as www.google.com:443/search/path?query=1&here=2
        :return: True if URL found to have malware in any database, False otherwise
        :rtype: bool
        """
        # TODO: Should an attempt be made to make urls be made uniform? (e.g. "evil.com" == "evil.com/"?)
        # TODO: Should urls be validated? (Do they need to be standards compliant?)
        # TODO: parallelize calls to several dbs
        for db in self._databases:
            if db.check_url_has_malware(host_and_query):
                return True
        return False

    def register_database(self, database: DatabaseABC):
        """Register a database with the url checker.

        Registering a database adds the database to the list of databases checked for malware
        :database DatabaseABC: A concrete subclass of DatabaseABC to register to the urlchecker
        :raises ValueError: In the case an invalid database adaptor is passed
        """
        if issubclass(type(database), DatabaseABC):
            self._databases.append(database)
        else:
            raise ValueError("Database is not an instance of DatabaseABC.")

    def get_db_count(self) -> int:
        return len(self._databases)
