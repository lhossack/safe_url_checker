"""
Defines config file parsing rules
"""
import json
import os
import logging
import typing

logger = logging.getLogger(__file__)


class ConfigReader:
    """Startup configuration reader

    Configuration defaults to read from same directory as config_reader.py
    Override this behaviour by exporting the environment variable "URLCHECK_CONFIG_PATH"
    or providing a configuration dictionary directly.

    See sphinx docs for a description of permissible configuration.

    :param config: configuration dictionary (python dictionary format, not json)
    :type config: dict, optional
    :raises OSError: OSError in the case the configuration file could not be accessed.
    """

    def __init__(self, config: dict = None) -> None:
        self.config_file = None
        startdir = os.curdir
        try:
            if not config:
                os.chdir(os.path.dirname(__file__))
                if "URLCHECK_CONFIG_PATH" in os.environ:
                    self.config_file = os.environ["URLCHECK_CONFIG_PATH"]
                else:
                    self.config_file = "../sample_resources/default_config.json"
                logger.info(
                    f"Attempting to load config from `{os.path.abspath(self.config_file)}`.."
                )
                with open(self.config_file) as conf_in:
                    self.config = json.load(conf_in)
            else:
                logger.info(f"Using dictionary config..")
                self.config = config
        finally:
            os.chdir(startdir)
        self.parse_config()

    def parse_config(self):
        """Read the configuration options from the config dictionary"""
        pass

    def get_config_source(self) -> typing.Tuple[str, str]:
        """Get the source of the configuration

        :return: ("dict", "") if config was passed directly, otherwise ("file", "filepath")
        :rtype: typing.Tuple[str, str]
        """
        if self.config_file is None:
            return ("dict", "")
        else:
            return ("file", self.config_file)

    def urlchecker(self):
        pass

    def databases(self):
        pass
