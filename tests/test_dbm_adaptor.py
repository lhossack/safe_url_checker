"""Tests for the dbm adaptor"""
import unittest
import unittest.mock
from context import dbm_adaptor
import dbm.dumb as dbm
from utils import mkTempDB, rmTempDB
import datetime
import os


class TestDbmCheckMalware(unittest.TestCase):
    """Check malware exists"""

    def setUp(self) -> None:
        mkTempDB(self)

    def tearDown(self) -> None:
        rmTempDB(self)

    def test_malware_exists(self):
        """Check returns "unsafe" when url is in malware database"""
        db = dbm_adaptor.DbmAdaptor("tmp/tmp")
        self.assertEqual(db.check_url_has_malware("www.evil.com")[0], "unsafe")
        self.assertEqual(
            db.check_url_has_malware("www.evil.com/index.html?q=download+ram")[0],
            "unsafe",
        )
        del db

    def test_malware_not_exists(self):
        """Check should return "safe" when records to not exist in db"""
        db = dbm_adaptor.DbmAdaptor("tmp/tmp")
        self.assertEqual(db.check_url_has_malware("www.good.com")[0], "safe")
        self.assertEqual(
            db.check_url_has_malware("www.3vil.com/index.html?q=download+ram")[0],
            "safe",
        )
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
        with dbm.open("tmp/tmp", "c", 0o666) as db2:
            db2[b"www.new-evil.com"] = b"Contains malware"
        self.assertEqual(db.check_url_has_malware("www.new-evil.com")[0], "safe")
        db.reload_database()
        self.assertEqual(db.check_url_has_malware("www.new-evil.com")[0], "unsafe")
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

        with dbm.open("tmp/tmp", "w", 0o666) as db2:
            db2[b"www.new-evil.com"] = b"Contains malware"
        self.assertEqual(db.check_url_has_malware("www.new-evil.com")[0], "safe")

        with unittest.mock.patch("dbm_adaptor.datetime.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = reload_time - datetime.timedelta(
                seconds=1
            )
            self.assertEqual(db.check_url_has_malware("www.new-evil.com")[0], "safe")

        with unittest.mock.patch("dbm_adaptor.datetime.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = reload_time + datetime.timedelta(
                seconds=1
            )
            self.assertEqual(db.check_url_has_malware("www.new-evil.com")[0], "unsafe")

        del db
        del db2


class TestConfigureFromDict(unittest.TestCase):
    """Verify configure from dict sets internal params properly"""

    def setUp(self) -> None:
        mkTempDB(self)

    def tearDown(self) -> None:
        rmTempDB(self)

    def test_config_from_dict_valid(self):
        """Verify internal config properly set"""
        db = dbm_adaptor.DbmAdaptor.configure_from_dict(
            {"filename": os.path.abspath("tmp/tmp"), "reload_time": 10}
        )
        self.assertEqual(db.filename, os.path.abspath("tmp/tmp"))
        self.assertEqual(db.reload_rate_minutes, 10)

    def test_config_from_dict_missing_inputs(self):
        """Verify config raises error on missing inputs"""
        with self.assertRaises(KeyError):
            db = dbm_adaptor.DbmAdaptor.configure_from_dict({"filename": "filename"})
        with self.assertRaises(KeyError):
            db = dbm_adaptor.DbmAdaptor.configure_from_dict({"reload_time": 10})


if __name__ == "__main__":
    unittest.main()
