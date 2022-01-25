"""
Defines abstract base class which database adaptors must conform to.
"""
import abc
import typing

DatabaseAbcT = typing.TypeVar("DatabaseAbcT", bound="DatabaseABC")


class DatabaseABC(metaclass=abc.ABCMeta):
    """Base class for URL malware status database adaptors"""

    @abc.abstractmethod
    def check_url_has_malware(self, host_and_query) -> typing.Tuple[str, str]:
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

    def check_any_url_has_malware(
        self, urls: typing.Iterable[str]
    ) -> typing.Tuple[str, str]:
        """Checks if url in urls is known to have malware

        Input query strings are of the form: "{hostname_and_port}/{original_path_and_query_string}".
        That is, they don't contain the protocol (e.g. "https://" is trimmed), but do include
        ports: e.g. https://www.google.com/search/path?query=1&here=2 should be passed in as
        www.google.com:443/search/path?query=1&here=2

        :param host_and_query: List of urls to check against the database.
        :type host_and_query: typing.Iterable[str]
        :return: ("unsafe", "malware") if *any* URL in urls found to have malware in this database, ("safe", "") otherwise
        :rtype: bool
        """
        for url in urls:
            response = self.check_url_has_malware(url)
            if response[0] == "unsafe":
                return response
        return ("safe", "")

    @abc.abstractclassmethod
    def configure_from_dict(cls, options) -> DatabaseAbcT:
        """Initialize and return a new database adaptor from a configuration dictionary

        :param options: The configuration dictionary of the form specified in the documentation for this database adaptor.
        :type options: dict, required
        :return: A concrete subclass of DatabaseABC
        :rtype: DatabaseABC
        """
        raise NotImplementedError
