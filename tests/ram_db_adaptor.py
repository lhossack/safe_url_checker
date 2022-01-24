from context import database_abc
import typing


class RamDbAdaptor(database_abc.DatabaseABC):
    """RAM based malware database"""

    def __init__(self) -> None:
        super().__init__()
        self.evil_urls = set()

    @classmethod
    def configure_from_dict(cls, options):
        raise NotImplementedError

    def add_malware_url(self, url) -> None:
        self.evil_urls.add(url)

    def check_url_has_malware(self, host_and_query) -> typing.Tuple[str, str]:
        if host_and_query in self.evil_urls:
            return ("unsafe", "malware")
        else:
            return ("safe", "")
