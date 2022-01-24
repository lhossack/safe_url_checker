"""
Tests to run against a server endpoint.
Endpoint must have the sample_resources data loaded in one of its databases during the test.

Note: Ensure the server is running before you run this test. 
Also set the environment variable: `URLINFO_SERVER` to the scheme, domain and port of the running server.
e.g. "http://localhost:5000". If the server is configured with TLS, these tests should continue to work properly.
"""
import unittest
import unittest.mock
import os
import requests


def get_evil_urls():
    sample_dir = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "sample_resources"
    )
    evil_urls = []
    for filename in ["sample.txt", "unsafe_urls.txt"]:
        with open(os.path.join(sample_dir, filename), "r") as fin:
            urls = fin.readlines()
        evil_urls.extend([x.strip() for x in urls])

    return evil_urls


def get_good_urls():
    return ["www.google.com", "www.amazon.com", "cisco.com"]


class TestUrlInfoService(unittest.TestCase):
    """Valid URL check tests"""

    def setUp(self) -> None:
        self.prefix = os.environ["URLINFO_SERVER"] + "/urlinfo/1/"

    def test_evil_urls_rejected(self):
        """Test all evil.com urls are rejected"""
        evil = get_evil_urls()
        for url in evil:
            response = requests.get(self.prefix + url)
            self.assertEqual(response.json()["status"], "unsafe")

    def test_good_urls_allowed(self):
        """Check malware is reported if malware is in configuration with 1 database, and not reported otherwise"""
        good = get_good_urls()

        for url in good:
            response = requests.get(self.prefix + url)
            self.assertEqual(response.json()["status"], "safe")

    def test_valid_api_endpoint(self):
        """Verify service responds with error on other endpoints"""
        response = requests.get(self.prefix + "/notvalid")
        self.assertEqual(response.json()["status"], "unknown")


if __name__ == "__main__":
    unittest.main()
