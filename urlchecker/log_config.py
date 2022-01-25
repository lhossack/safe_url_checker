from logging.config import dictConfig
import os

if "URLINFO_LOGLEVEL" in os.environ and os.environ["URLINFO_LOGLEVEL"] in [
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]:
    LOGLEVEL = os.environ["URLINFO_LOGLEVEL"]
else:
    LOGLEVEL = "WARNING"

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)s %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            },
            "default": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
                "formatter": "default",
            },
        },
        "loggers": {
            "urlchecker": {
                "handlers": ["default"],
                "level": LOGLEVEL,
                "propagate": False,
            },
            "dbm_adaptor": {
                "handlers": ["default"],
                "level": LOGLEVEL,
                "propagate": False,
            },
        },
        "root": {"level": LOGLEVEL, "handlers": ["wsgi"]},
    }
)
