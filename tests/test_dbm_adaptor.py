"""Tests for the dbm adaptor"""
import unittest
import unittest.mock
from context import dbm_adaptor
import dbm.dumb as dbm
from utils import mkTempDB, rmTempDB
import datetime

class TestDbmCheckMalware(unittest.TestCase):
    """Check malware exists"""
    def setUp(self) -> None:
        mkTempDB(self)

    def tearDown(self) -> None:
        rmTempDB(self)

    def test_malware_exists(self):
        """Check returns True when record exists"""
        db = dbm_adaptor.DbmAdaptor("tmp/tmp")
        self.assertTrue(db.check_url_has_malware("www.evil.com"))
        self.assertTrue(db.check_url_has_malware("www.evil.com/index.html?q=download+ram"))
        del db

    def test_malware_not_exists(self):
        """Check should return False when records to not exist in db"""
        db = dbm_adaptor.DbmAdaptor("tmp/tmp")
        self.assertFalse(db.check_url_has_malware("www.good.com"))
        self.assertFalse(db.check_url_has_malware("www.3vil.com/index.html?q=download+ram"))
        del db


class TestDbmReloadAccess(unittest.TestCase):
    """Valid URL check tests"""
    def setUp(self) -> None:
        mkTempDB(self)

    def tearDown(self) -> None:
        rmTempDB(self)

    def test_concurrent_open_read_only_file(self):
        """Multiple processes and threads can have this file open for read using dbm."""
        try:
            db = dbm_adaptor.DbmAdaptor("tmp/tmp")
            db2 = dbm_adaptor.DbmAdaptor("tmp/tmp")
            del db
            del db2
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")

    def test_update_reload(self):
        """Test reload behavior updates database"""
        db = dbm_adaptor.DbmAdaptor("tmp/tmp")
        with dbm.open("tmp/tmp", 'c', 0o666) as db2:
            db2[b"www.new-evil.com"] = b"Contains malware"
        self.assertFalse(db.check_url_has_malware("www.new-evil.com"))
        db.reload_database()
        self.assertTrue(db.check_url_has_malware("www.new-evil.com"))
        del db
        del db2

class TestReloadCooldown(unittest.TestCase):
    """Verify cooldown/ timed refresh works properly"""
    def setUp(self) -> None:
        mkTempDB(self)

    def tearDown(self) -> None:
        rmTempDB(self)

    def test_reload_cooldown(self):
        """Test reload timeout causes updates to database on next query"""
        db = dbm_adaptor.DbmAdaptor("tmp/tmp", 10)
        reload_time = db.reload_time

        with dbm.open("tmp/tmp", 'w', 0o666) as db2:
            db2[b"www.new-evil.com"] = b"Contains malware"
        self.assertFalse(db.check_url_has_malware("www.new-evil.com"))

        with unittest.mock.patch(
                "dbm_adaptor.datetime.datetime"
            ) as mock_datetime:
            mock_datetime.utcnow.return_value = reload_time - datetime.timedelta(seconds=1)
            self.assertFalse(db.check_url_has_malware("www.new-evil.com"))

        with unittest.mock.patch(
                "dbm_adaptor.datetime.datetime"
            ) as mock_datetime:
            mock_datetime.utcnow.return_value = reload_time + datetime.timedelta(seconds=1)
            self.assertTrue(db.check_url_has_malware("www.new-evil.com"))

        del db
        del db2


if __name__ == '__main__':
    unittest.main()