import unittest
import unittest.mock
from context import urlchecker
import db_stub


class TestUrlCheckerHasMalware(unittest.TestCase):
    """Valid URL check tests"""
    def test_no_db(self):
        """Ensure malware is not reported when there are no databases attached"""
        checker = urlchecker.UrlChecker()
        self.assertFalse(checker.check_url_has_malware("hostname:port/path"))

    def test_single_db(self):
        """Check malware is reported if malware is in configuration with 1 database, and not reported otherwise"""
        checker = urlchecker.UrlChecker()
        mem_db = db_stub.MalwareDbStub()
        mem_db.add_malware_url("evil.com")
        mem_db.add_malware_url("evil.com/path")
        checker.register_database(mem_db)

        self.assertTrue(checker.check_url_has_malware("evil.com"))
        self.assertTrue(checker.check_url_has_malware("evil.com/path"))
        self.assertFalse(checker.check_url_has_malware("good.com"))
        self.assertFalse(checker.check_url_has_malware("good.com/path"))

    def test_multiple_db(self):
        """Check malware is reported if it is in any database, and not reported otherwise"""
        checker = urlchecker.UrlChecker()

        mem_db = db_stub.MalwareDbStub()
        mem_db.add_malware_url("evil.com")
        mem_db.add_malware_url("evil.com/path")

        mem_db2 = db_stub.MalwareDbStub()
        mem_db2.add_malware_url("eve.com/evil_path?q=bad")

        mem_db3 = db_stub.MalwareDbStub()
        mem_db3.add_malware_url("lucifer.com")

        checker.register_database(mem_db)
        checker.register_database(mem_db2)
        checker.register_database(mem_db3)

        self.assertTrue(checker.check_url_has_malware("evil.com"))
        self.assertTrue(checker.check_url_has_malware("evil.com/path"))
        self.assertTrue(checker.check_url_has_malware("eve.com/evil_path?q=bad"))
        self.assertTrue(checker.check_url_has_malware("lucifer.com"))

        self.assertFalse(checker.check_url_has_malware("good.com"))
        self.assertFalse(checker.check_url_has_malware("lucifer.com/good_path"))


class TestUrlCheckerDbRegistration(unittest.TestCase):
    """Verify database registration to UrlChecker"""
    def test_valid_db(self):
        """Check each time a database is registered it is added to the databases"""
        checker = urlchecker.UrlChecker()
        db = db_stub.MalwareDbStub()
        checker.register_database(db)
        self.assertEqual(1, checker.get_db_count())
        checker.register_database(db)
        self.assertEqual(2, checker.get_db_count())

    def test_invalid_db(self):
        """Check that invalid databases (non-subclasses of databaseABC) are rejected at registration"""
        class InvalidDbStub:
            pass
        
        invalid_db = InvalidDbStub()
        checker = urlchecker.UrlChecker()
        with self.assertRaises(ValueError):
            checker.register_database(invalid_db)

    def test_invalid_db_on_init(self):
        """Check that invalid databases (non-subclasses of databaseABC) are rejected during UrlChecker init"""
        class InvalidDbStub:
            pass
        
        invalid_db = InvalidDbStub()
        with self.assertRaises(ValueError):
            urlchecker.UrlChecker(databases = [invalid_db])


if __name__ == '__main__':
    unittest.main()