import config_reader
import os

import werkzeug
from flask import Flask, request, jsonify
from logging.config import dictConfig

if "URLINFO_LOGLEVEL" in os.environ and os.environ["URLINFO_LOGLEVEL"] in [
    "INFO",
    "DEBUG",
    "WARN",
    "ERROR",
    "CRITICAL",
]:
    LOGLEVEL = os.environ["URLINFO_LOGLEVEL"]
else:
    LOGLEVEL = "WARN"

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
            }
        },
        "loggers": {
            "urlchecker": {"handlers": ["wsgi"], "level": LOGLEVEL, "propagate": False},
            "dbm_adaptor": {
                "handlers": ["wsgi"],
                "level": LOGLEVEL,
                "propagate": False,
            },
        },
        "root": {"level": LOGLEVEL, "handlers": ["wsgi"]},
    }
)


def create_app(test_config=None):
    """Create and return flask application

    Defines route handlers, which pass off control almost immediately
    once done with flask-specific code to handle IO
    """
    app = Flask(__name__)

    urlchecker_cfg = config_reader.ConfigReader()
    urlchecker_cfg.configure()
    urlchecker = urlchecker_cfg.urlchecker

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config["TRAP_HTTP_EXCEPTIONS"] = True

    @app.errorhandler(Exception)
    def handle_error(e):
        """Return error for anything other than urlinfo/1/ route, or on any unhandled exception"""
        app.logger.exception(f"Application exception: {e.code}", exc_info=e)
        try:
            return (jsonify({"status": "unknown", "reason": "invalid request"}), e.code)
        except:
            return (jsonify({"status": "unknown", "reason": "server error"}), 500)

    @app.route("/urlinfo/1/<path:hostpath>", methods=["GET"])
    def urlinfo(hostpath):
        """The main route for urlchecker interface"""
        urldata = request.full_path[len("/urlinfo/1/") :]

        # Werkzeug appends a '?' when there are no query params
        if urldata.endswith("?"):
            urldata = urldata[:-1]

        status, reason = urlchecker.check_url_has_malware(
            werkzeug.urls.iri_to_uri(urldata)
        )

        return jsonify({"status": status, "reason": reason})

    return app
