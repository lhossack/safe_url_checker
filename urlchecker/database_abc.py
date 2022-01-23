"""
Defines abstract base class which database adaptors must conform to.
"""
import abc


class DatabaseABC(metaclass=abc.ABCMeta):
    """Base class for URL malware status database adaptors"""

    @abc.abstractmethod
    def check_url_has_malware(self, host_and_query) -> bool:
        """Checks if url is known to have malware

        Input query strings are of the form: "{hostname_and_port}/{original_path_and_query_string}".
        That is, they don't contain the protocol (e.g. "https://" is trimmed), but may include
        ports: e.g. https://www.google.com/search/path?query=1&here=2 should be passed in as
        www.google.com:443/search/path?query=1&here=2

        :param str host_and_query: Host and query
        :return: True if URL found to have malware in this database, False otherwise
        :rtype: bool
        """
        raise NotImplementedError
