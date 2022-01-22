import unittest
from context import urlchecker

class TestUrlCheckerValidateUrl(unittest.TestCase):
    """Valid URL check tests"""
    def test_invalid_urls(self):
        self.assertFalse(urlchecker.UrlChecker.validate_url("hostname:port/ invalid_space"))

    def test_valid_urls(self):
        self.assertTrue(urlchecker.UrlChecker.validate_url("hostname:port/valid_url"))

if __name__ == '__main__':
    unittest.main()