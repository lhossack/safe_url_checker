# Assumptions

## Assumptions about input URLs
- Databases store information about full URLs (including hostname, port, and query string)
    e.g. good.com/ (root path/ index) may not contain malware
    but good.com/evil/path?evil=query may contain malware. 
    The service will not prevent access to good.com, but will prevent access to good.com

- URLs may be malformed but still sent through the proxy.
    In this case, this url checking service shouldn't be blocking or returning errors for these URLs since some servers may be able to handle URLs that do not obey the relevant RFCs for URLs.
    
    @unittest.skip("Assuming this functionality should not be added.")
    class TestUrlCheckerValidateUrl(unittest.TestCase):
        """Valid URL check tests"""
        def test_invalid_urls(self):
            self.assertFalse(urlchecker.UrlChecker.validate_url("hostname:port/ invalid_space"))

        def test_valid_urls(self):
            self.assertTrue(urlchecker.UrlChecker.validate_url("hostname:port/valid_url"))


## Changes from initial email
I am using dbm.dumb instead of dbm.gnu databases. This makes the files more portable (does not require external libraries), but provides lower performance. Additionally, there can be multiple readers and a single writer which will allow for changes to the file to be made while running (the file will need to be reloaded periodically to receive updates).
