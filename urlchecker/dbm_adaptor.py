"""dbm based url malware lookup database"""
from imp import reload
from urlchecker.database_abc import DatabaseABC, DatabaseAbcT
import dbm.dumb as dbm  # Used for platform compatibility
import weakref
import datetime
import typing

import logging

logger = logging.getLogger(__name__)

DbmAdaptorT = typing.TypeVar("DbmAdaptorT", bound="DbmAdaptor")


class DbmAdaptor(DatabaseABC):
    """Manage dbm queries to a single database

    One instance should exist per file object. dbm cannot support parallel access.

    :param str filename: path/name of the dbm database to open
    :raises OSError: In the case the database file cannot be opened
    """

    def __init__(
        self, filename: str, reload_rate_minutes: typing.Union[int, None] = 10
    ) -> None:
        self.filename = filename
        self.reload_rate_minutes = reload_rate_minutes
        self.reload_time = datetime.datetime.utcnow()
        self.reload_database()

    @classmethod
    def configure_from_dict(cls, options: dict) -> DbmAdaptorT:
        """Alternative constructor using options from from a configuration dictionary

        :param options: The configuration dictionary of the form specified in the documentation for this database adaptor.
        :type options: dict, required
        :return: A concrete subclass of DatabaseABC
        :rtype: DatabaseABC
        """
        filename = str(options["filename"])
        if options["reload_time"]:
            reload_time = int(options["reload_time"])
        else:
            reload_time = None
        return cls(filename, reload_rate_minutes=reload_time)

    def check_url_has_malware(self, host_and_query: str) -> bool:
        """Check if url is associated with malware in this database.

        :param str host_and_query: Host and query string (e.g. "www.google.com/search/1/?q=search+term")
        :return: True if URL found to have malware in any database, False otherwise
        :rtype: bool
        """
        self.reload_db_if_needed()
        try:
            byte_key = host_and_query.encode(encoding="utf-8", errors="strict")
        except ValueError:
            logger.info(f"Failed to encode URL: {host_and_query}")
            return True  # TODO: Check assumption: should this return True or False? Config option?

        if byte_key in self.db:
            return True
        else:
            return False

    def reload_db_if_needed(self):
        """Reload the database from filesystem if past the cooldown time"""
        if (
            self.reload_rate_minutes is not None
            and datetime.datetime.utcnow() >= self.reload_time
        ):
            self.reload_database()

    def reload_database(self):
        """Load or reload the database from memory.

        :raises OSError: In the case the database file cannot be opened
        """
        if self.reload_rate_minutes is not None:
            self.reload_time = datetime.datetime.utcnow() + datetime.timedelta(
                minutes=self.reload_rate_minutes
            )
        self.db = dbm.open(self.filename, "r")

        def close(db, filename):
            db.close()
            logger.info(f"Database (dbm) closed: {self.filename}")

        weakref.finalize(
            self, close, self.db, self.filename
        )  # Ensure db is closed properly later
        logger.info(f"Database (dbm) loaded: {self.filename}")
