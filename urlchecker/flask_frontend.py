import log_config
import config_reader
import os

import werkzeug
from flask import Flask, request, jsonify


def create_app(test_config=None):
    """Create and return flask application

    Defines route handlers, which pass off control almost immediately
    once done with flask-specific code to handle IO
    """

    urlchecker_cfg = config_reader.ConfigReader()
    urlchecker_cfg.configure()
    urlchecker = urlchecker_cfg.urlchecker

    app = Flask(__name__)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config["TRAP_HTTP_EXCEPTIONS"] = True

    @app.errorhandler(Exception)
    def handle_error(e):
        """Return error for anything other than urlinfo/1/ route, or on any unhandled exception"""
        try:
            app.logger.info(f"Client or server error {e.code}", exc_info=e)
            return (jsonify({"status": "unknown", "reason": "invalid request"}), e.code)
        except:
            app.logger.exception(f"Application exception: ", exc_info=e)
            return (jsonify({"status": "unknown", "reason": "server error"}), 500)

    @app.route("/urlinfo/1/<path:hostpath>", methods=["GET"])
    def urlinfo(hostpath):
        """The main route for urlchecker interface"""
        app.logger.debug(f"Request: {hostpath}")
        urldata = request.full_path[len("/urlinfo/1/") :]

        # Werkzeug appends a '?' when there are no query params
        if urldata.endswith("?"):
            urldata = urldata[:-1]

        app.logger.debug(f"Checking: '{werkzeug.urls.iri_to_uri(urldata)}'")
        status, reason = urlchecker.check_url_has_malware(
            werkzeug.urls.iri_to_uri(urldata)
        )
        response = jsonify({"status": status, "reason": reason})
        app.logger.debug(f"Response: {response}")
        return response

    return app
