from context import config_reader
import json
import shutil
import unittest
import unittest.mock
import os
from urlchecker.database_abc import DatabaseABC
from utils import mkTempDB, rmTempDB
import dbm.dumb


class TestConfigReader(unittest.TestCase):
    """Check config reader can handle configuration inputs"""

    def test_passed_dictionary(self):
        """Check config reader properly handles config passed directly to init"""
        cfg_reader = config_reader.ConfigReader({"databases": []})
        config_src, _ = cfg_reader.get_config_source()
        self.assertEqual(config_src, "dict")

    def test_default_config(self):
        """Check default config is loaded when no arguments passed"""
        cfg_reader = config_reader.ConfigReader()
        config_src, _ = cfg_reader.get_config_source()
        self.assertEqual(config_src, "file")

    def test_file_environ_config(self):
        """Check gets config from given file via environment variable"""
        tmpdir = os.path.join(os.path.dirname(__file__), "tmp_config")
        os.makedirs(tmpdir, exist_ok=True)
        tmpfile = os.path.join(tmpdir, "config.json")
        try:
            os.environ["URLINFO_CONFIG"] = os.path.abspath(tmpfile)
            with open(tmpfile, "w") as conf:
                json.dump({"databases": []}, conf)
            cfg_reader = config_reader.ConfigReader()
            config_src, filename = cfg_reader.get_config_source()
            self.assertEqual(config_src, "file")
            self.assertTrue(os.path.samefile(tmpfile, filename))
        finally:
            del os.environ["URLINFO_CONFIG"]
            shutil.rmtree(tmpdir)

    def test_bad_path_environ(self):
        """Test config fails to load and raises exception when pointed at a non existent path"""
        tmpfile = os.path.join(os.path.dirname(__file__), "tmp/nonexistent/path")
        try:
            os.environ["URLINFO_CONFIG"] = os.path.abspath(tmpfile)
            with self.assertRaises(OSError):
                cfg_reader = config_reader.ConfigReader()
        finally:
            del os.environ["URLINFO_CONFIG"]

    def test_relative_path_environ(self):
        """Test ConfigReader properly handles relative paths to config files"""
        startdir = os.getcwd()
        cfg_dir_path = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(cfg_dir_path, exist_ok=True)
        cfg_path = os.path.join(cfg_dir_path, "config.json")
        db_path = os.path.join(cfg_dir_path, "tmp_db")

        with open(cfg_path, "w") as fout:
            json.dump(
                {
                    "databases": [
                        {
                            "type": "dbm.dumb",
                            "options": {
                                "filename": os.path.relpath(
                                    db_path, os.path.dirname(cfg_path)
                                ),
                                "reload_time": 10,
                            },
                        }
                    ]
                },
                fout,
            )
        with dbm.dumb.open(db_path, "c", 0o666) as db:
            db[b"www.test.com"] = b"test data"
            db[b"www.sample.ca"] = b"malware"

        rel_path = os.path.relpath(cfg_path, os.path.dirname(config_reader.__file__))

        try:
            os.environ["URLINFO_CONFIG"] = rel_path
            cfg_reader = config_reader.ConfigReader()
            dbs = cfg_reader.configure_all_databases()
            self.assertEqual(len(dbs), 1)
            self.assertTrue(issubclass(type(dbs[0]), DatabaseABC))
        finally:
            del os.environ["URLINFO_CONFIG"]
            os.chdir(startdir)
            shutil.rmtree(cfg_dir_path)


class TestConfigReaderParser(unittest.TestCase):
    """Validate config dictionary parsing"""

    def test_no_databases(self):
        """Ensure ValueError raised when there are no databases in configuration"""
        with self.assertRaises(ValueError):
            cfg_reader = config_reader.ConfigReader({"databases": []})
            cfg_reader.configure()

        with self.assertRaises(ValueError):
            cfg_reader = config_reader.ConfigReader({"someotherkey": "and value"})
            cfg_reader.configure()


class TestConfigureDatabaseParser(unittest.TestCase):
    """Test database specific parsing"""

    def setUp(self) -> None:
        mkTempDB(self)

    def tearDown(self) -> None:
        rmTempDB(self)

    def test_db_type_dbm_dumb(self):
        """Test creating dbm.dumb databases using config reader"""
        cfg = config_reader.ConfigReader(
            {
                "databases": [
                    {
                        "type": "dbm.dumb",
                        "options": {
                            "filename": os.path.abspath("tmp/tmp"),
                            "reload_time": 10,
                        },
                    },
                    {
                        "type": "dbm.dumb",
                        "options": {
                            "filename": os.path.abspath("tmp/tmp"),
                            "reload_time": None,
                        },
                    },
                ]
            }
        )
        dbs = cfg.configure_all_databases()
        self.assertGreater(len(dbs), 0)
        for db in dbs:
            self.assertTrue(isinstance(db, DatabaseABC))

    def test_db_type_not_exists(self):
        """Test ValueError raised when database type does not exist/ can't load database"""
        cfg = config_reader.ConfigReader(
            {
                "databases": [
                    {
                        "type": "not a database type",
                        "options": {},
                    }
                ]
            }
        )
        with self.assertRaises(ValueError):
            cfg.configure_all_databases()

    def test_db_missing_opts(self):
        """Test missing options for database test raises error"""
        cfg = config_reader.ConfigReader(
            {
                "databases": [
                    {
                        "type": "dbm.dumb",
                    }
                ]
            }
        )
        with self.assertRaises(Exception):
            cfg.configure_all_databases()


if __name__ == "__main__":
    unittest.main()
