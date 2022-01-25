"""
Defines config file parsing rules
"""
import copy
import json
import os
import logging
import typing
import dbm_adaptor
from urlchecker import mongo_adaptor, urlchecker
import database_abc

logger = logging.getLogger(__name__)


class ConfigReader:
    """Startup configuration reader

    Configuration defaults to read from same directory as config_reader.py
    Override this behaviour by exporting the environment variable "URLINFO_CONFIG"
    or providing a configuration dictionary directly.

    See sphinx docs for a description of permissible configuration.

    General usage:

    1. Initialize ConfigReader to load the configuration file: cfg = ConfigReader()
    2. Call cfg.configure() to parse the configuration file
    3. cfg.urlchecker is the configured urlchecker


    :param config: configuration dictionary (python dictionary format, not json)
    :type config: dict, optional
    :raises OSError: OSError in the case the configuration file could not be accessed.
    """

    def __init__(self, config: dict = None) -> None:
        self.config_file = ""
        self.config_dir = ""
        if config:
            logger.info(f"Using dictionary config..")
            self.config = config
        else:
            if "URLINFO_CONFIG" in os.environ:
                self.config_file = os.environ["URLINFO_CONFIG"]
            else:
                self.config_file = "../sample_resources/default_config.json"
            self.config = self.load_from_file()

    def load_from_file(self):
        """Load configuration from file (default or in os.environ["URLINFO_CONFIG"])

        :return: configuration dict from file
        :rtype: dict
        :raises OSError: In the case the configuration file could not be accessed.
        """
        startdir = os.getcwd()
        try:
            os.chdir(os.path.dirname(__file__))
            logger.info(
                f"Attempting to load config from `{os.path.abspath(self.config_file)}`.."
            )
            self.config_dir = os.path.dirname(os.path.abspath(self.config_file))
            with open(self.config_file) as conf_in:
                config = json.load(conf_in)
        except Exception:
            raise OSError(f"Could not load config from: {self.config_file}")
        finally:
            os.chdir(startdir)
        return config

    def get_config_source(self) -> typing.Tuple[str, str]:
        """Get the source of the configuration

        :return: ("dict", "") if config was passed directly, otherwise ("file", "filepath")
        :rtype: typing.Tuple[str, str]
        """
        if self.config_file:
            return ("file", self.config_file)
        else:
            return ("dict", "")

    def configure(self):
        """Create app as per configuration in config dict

        self.config must exist prior to this call.
        :raises ValueError: For any critical issue related to startup with the current configuration
        """
        databases = self.configure_all_databases()

        self.urlchecker = urlchecker.UrlChecker(databases=databases)

    def configure_all_databases(self) -> typing.List[database_abc.DatabaseABC]:
        """Configure all databases from loaded config dictionary

        :return: List of database objects initiated from config file
        :rtype: typing.List[database_abc.DatabaseABC]
        :raises ValueError: if no databases are in the configuration or there is an issue loading a database
        """
        databases = []
        if "databases" in self.config and isinstance(
            self.config["databases"], typing.Iterable
        ):
            startdir = os.getcwd()
            if self.config_dir:
                os.chdir(self.config_dir)
            try:
                if len(self.config["databases"]) < 1:
                    raise ValueError("No databases in configuration!")
                for db_config in self.config["databases"]:
                    try:
                        databases.append(self.configure_database(db_config))
                    except Exception as e:
                        raise ValueError(f"Error loading database: {db_config}")
            finally:
                if self.config_dir:
                    os.chdir(startdir)
            return databases
        raise ValueError("No 'databases' in config!")

    @staticmethod
    def configure_database(db_config) -> database_abc.DatabaseABC:
        """Database factory. Generates databases from config.

        Calls specific database adaptor handlers and registers constructs to urlchecker

        :param db_config: database configuration dictionary; see sphinx config docs for more information
        :type db_config: dict, required
        :return: Concrete subclass implementing DatabaseABC of type given in db_config
        :rtype: database_abc.DatabaseABC
        :raises ValueError: if database type is not recognized
        """
        if "type" in db_config and type(db_config["type"]) == str:
            if db_config["type"] == "dbm.dumb":
                return dbm_adaptor.DbmAdaptor.configure_from_dict(db_config["options"])
            elif db_config["type"] == "mongo":
                options_copy = copy.deepcopy(db_config["options"])
                try:
                    options_copy["connection_string"] = os.environ[
                        db_config["options"]["connection_string"]
                    ]
                    options_copy["username"] = os.environ[
                        db_config["options"]["username"]
                    ]
                    options_copy["password"] = os.environ[
                        db_config["options"]["password"]
                    ]
                except KeyError as e:
                    logger.error(
                        "Could not read environment variables or username/password missing",
                        exc_info=e,
                    )
                    raise ValueError("Issue with mongo database configuration")
                return mongo_adaptor.MongoAdaptor.configure_from_dict(options_copy)
        raise ValueError(f"{db_config['type']} is not a recognized database type")
