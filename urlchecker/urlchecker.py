from .databaseABC import DatabaseABC
import typing

class UrlChecker:
    """Manages checking URLs against databases of URLs known to contain malware.
    """
    def __init__(self, databases: typing.List[DatabaseABC] = None) -> None:
        if databases:
            self.databases = databases
        else:
            self.databases = []
        
    def is_url_safe(self, host_and_query_str: str):
        """Checks url safety against all registered databases.

        :param str host_and_query: Host and query in format: {hostname_and_port}/{original_path_and_query_string} That is, they don't contain the protocol (e.g. "https://" is trimmed), but may include ports: e.g. https://www.google.com/search/path?query=1&here=2 should be passed in as www.google.com:443/search/path?query=1&here=2
        :return: True if URL not found in any malicious URL databases, False otherwise
        :rtype: bool
        :raises ValueError: if the message_body exceeds 160 characters
        """
        pass

    @staticmethod
    def validate_url(host_and_query: str):
        """Validates URL host_and_query is a valid format.
        
        :param str host_and_query: Host and query in format: {hostname_and_port}/{original_path_and_query_string}
        :return: True if host_and_query is a valid URL format, False otherwise.
        :rtype: bool
        """
        return True

    def register_database(self, database: DatabaseABC):
        pass

