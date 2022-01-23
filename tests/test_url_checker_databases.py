import unittest
import unittest.mock
import ram_db_adaptor
from context import urlchecker, dbm_adaptor
import utils
import copy


class TestUrlCheckerDbmDbs(unittest.TestCase):
    """Check URLs valid in dbm through TestUrlChecker"""

    def setUp(self) -> None:
        utils.mkTempDB(self)

    def tearDown(self) -> None:
        utils.rmTempDB(self)

    def test_multiple_different_dbs(self):
        """Check malware is reported if it is in any database, and not reported otherwise"""
        checker = urlchecker.UrlChecker()

        dbm_db = dbm_adaptor.DbmAdaptor("tmp/tmp")
        checker.register_database(dbm_db)

        mem_db = ram_db_adaptor.RamDbAdaptor()
        for url in utils.memory_urls:
            mem_db.add_malware_url(url)
        checker.register_database(mem_db)

        all_evil_urls = copy.copy(utils.dbm_malware_urls)
        all_evil_urls.extend(utils.memory_urls)

        for url in all_evil_urls:
            self.assertTrue(checker.check_url_has_malware(url))

        self.assertFalse(checker.check_url_has_malware("good.com"))
        self.assertFalse(checker.check_url_has_malware("lucifer.com/good_path"))


if __name__ == "__main__":
    unittest.main()
