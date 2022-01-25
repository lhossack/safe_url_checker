import unittest
import unittest.mock
from context import urlchecker
import ram_db_adaptor
import utils


class TestDatabaseABCAnyUrlHasMalware(unittest.TestCase):
    """Valid URL check tests for list of urls (check_any_url_has_malware)"""

    def test_no_db(self):
        """Ensure malware is not reported when there are no urls"""
        mem_db = ram_db_adaptor.RamDbAdaptor()
        mem_db.add_malware_url("evil.com")
        mem_db.add_malware_url("evil.com/path")

        self.assertEqual(mem_db.check_any_url_has_malware([])[0], "safe")

    def test_all_db_in_list_safe(self):
        """Ensure malware is not reported when there are no unsafe urls"""
        mem_db = ram_db_adaptor.RamDbAdaptor()
        mem_db.add_malware_url("evil.com")
        mem_db.add_malware_url("different-evil-place.com/path")

        to_check = ["safe.com", "not-evil.com"]
        self.assertEqual(mem_db.check_any_url_has_malware(to_check)[0], "safe")

    def test_one_malicious_db_in_list(self):
        """Ensure malware is reported when there is at least 1 unsafe url"""
        mem_db = ram_db_adaptor.RamDbAdaptor()
        mem_db.add_malware_url("evil.com")
        mem_db.add_malware_url("different-evil-place.com/path")

        to_check = ["safe.com", "not-evil.com", "different-evil-place.com"]

        self.assertEqual(mem_db.check_any_url_has_malware(to_check)[0], "safe")


if __name__ == "__main__":
    unittest.main()
