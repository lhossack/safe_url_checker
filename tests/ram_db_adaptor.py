from context import database_abc


class RamDbAdaptor(database_abc.DatabaseABC):
    """RAM based malware database"""

    def __init__(self) -> None:
        super().__init__()
        self.evil_urls = set()

    def add_malware_url(self, url) -> None:
        self.evil_urls.add(url)

    def check_url_has_malware(self, host_and_query) -> bool:
        if host_and_query in self.evil_urls:
            return True
        else:
            return False