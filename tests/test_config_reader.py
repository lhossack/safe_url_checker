import json
import shutil
import unittest
import unittest.mock
from context import config_reader
import os


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
            os.environ["URLCHECK_CONFIG_PATH"] = os.path.abspath(tmpfile)
            with open(tmpfile, "w") as conf:
                json.dump({"databases": []}, conf)
            cfg_reader = config_reader.ConfigReader()
            config_src, filename = cfg_reader.get_config_source()
            self.assertEqual(config_src, "file")
            self.assertTrue(os.path.samefile(tmpfile, filename))
        finally:
            del os.environ["URLCHECK_CONFIG_PATH"]
            shutil.rmtree(tmpdir)

    def test_bad_path_environ(self):
        tmpfile = os.path.join(os.path.dirname(__file__), "tmp/nonexistent/path")
        try:
            os.environ["URLCHECK_CONFIG_PATH"] = os.path.abspath(tmpfile)
            with self.assertRaises(FileNotFoundError):
                cfg_reader = config_reader.ConfigReader()
        finally:
            del os.environ["URLCHECK_CONFIG_PATH"]


class TestConfigReaderParser(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
