"""dbm based url malware lookup database"""
from imp import reload
from urlchecker.database_abc import DatabaseABC
import dbm.dumb as dbm  # Used for platform compatibility
import weakref
import datetime

import logging

logger = logging.getLogger(__name__)


class DbmAdaptor(DatabaseABC):
    """Manage dbm queries to a single database

    One instance should exist per file object. dbm cannot support parallel access.

    :param str filename: path/name of the dbm database to open
    :raises OSError: In the case the database file cannot be opened
    """

    def __init__(self, filename: str, reload_rate_minutes: int = 10) -> None:
        self.filename = filename
        self.reload_rate_minutes = reload_rate_minutes
        self.reload_time = datetime.datetime.utcnow()
        self.reload_db_if_needed()

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
        if datetime.datetime.utcnow() >= self.reload_time:
            self.reload_database()
            self.reload_time = datetime.datetime.utcnow() + datetime.timedelta(
                minutes=self.reload_rate_minutes
            )

    def reload_database(self):
        """Load or reload the database from memory.

        :raises OSError: In the case the database file cannot be opened
        """
        self.db = dbm.open(self.filename, "r")

        def close(db, filename):
            db.close()
            logger.info(f"Database (dbm) closed: {self.filename}")

        weakref.finalize(
            self, close, self.db, self.filename
        )  # Ensure db is closed properly later
        logger.info(f"Database (dbm) loaded: {self.filename}")
