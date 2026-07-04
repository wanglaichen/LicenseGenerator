from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException
import os

from api import api_bp
from config import AppConfig

app = Flask(__name__)
app.config.from_object(AppConfig)
app.register_blueprint(api_bp)


@app.route("/")
def index():
    return render_template(
        "index.html",
        default_sn=app.config["DEFAULT_SN"],
        default_key=app.config["REGISTER_KEY"],
    )


@app.errorhandler(ValueError)
def handle_value_error(error):
    return jsonify({"message": str(error)}), 400


@app.errorhandler(HTTPException)
def handle_http_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"message": error.description}), error.code
    return error


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception("Unhandled error")
    if request.path.startswith("/api/"):
        return jsonify({"message": str(error)}), 500
    raise error


if __name__ == "__main__":
    debug_enabled = os.getenv("APP_DEBUG", "0") == "1"
    app.run(
        debug=debug_enabled,
        use_reloader=False,
        host=app.config["APP_HOST"],
        port=app.config["APP_PORT"],
    )
