from flask import current_app, jsonify, request

from api import api_bp
from services.register_service import (
    generate_machine_md5_payload,
    generate_payload,
    generate_register_payload,
)


def _parse_md5_length(raw_value) -> int | None:
    if raw_value is None or raw_value == "":
        return None
    return int(raw_value)


@api_bp.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@api_bp.route("", methods=["GET"])
def api_index():
    return jsonify(
        {
            "name": "RegMachine Web API",
            "version": "1.0",
            "endpoints": {
                "health": {"method": "GET", "path": "/api/health"},
                "machine_md5": {
                    "method": "POST",
                    "path": "/api/machine-md5",
                    "body": {
                        "machine_code": "string, required",
                        "md5_length": "integer, optional, default = machine_code byte length",
                    },
                },
                "register_code": {
                    "method": "POST",
                    "path": "/api/register-code",
                    "body": {
                        "sn": "string, required",
                        "key": "string, optional, 8 bytes, default from server config",
                    },
                },
                "generate": {
                    "method": "POST",
                    "path": "/api/generate",
                    "body": {
                        "machine_code": "string, required",
                        "sn": "string, required",
                        "key": "string, optional, 8 bytes, default from server config",
                        "md5_length": "integer, optional",
                    },
                },
            },
        }
    )


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "regmachine-web",
            "default_key": current_app.config["REGISTER_KEY"],
        }
    )


@api_bp.route("/machine-md5", methods=["POST", "OPTIONS"])
def machine_md5_route():
    if request.method == "OPTIONS":
        return "", 204

    payload = request.get_json(silent=True) or {}
    return jsonify(
        generate_machine_md5_payload(
            machine_code=payload.get("machine_code", ""),
            md5_length=_parse_md5_length(payload.get("md5_length")),
        )
    )


@api_bp.route("/register-code", methods=["POST", "OPTIONS"])
def register_code_route():
    if request.method == "OPTIONS":
        return "", 204

    payload = request.get_json(silent=True) or {}
    sn = payload.get("sn", "")
    key = payload.get("key") or current_app.config["REGISTER_KEY"]
    return jsonify(generate_register_payload(sn=sn, key=key))


@api_bp.route("/generate", methods=["POST", "OPTIONS"])
def generate():
    if request.method == "OPTIONS":
        return "", 204

    payload = request.get_json(silent=True) or {}
    machine_code = payload.get("machine_code", "")
    sn = payload.get("sn", "")
    key = payload.get("key") or current_app.config["REGISTER_KEY"]
    return jsonify(
        generate_payload(
            machine_code=machine_code,
            sn=sn,
            key=key,
            md5_length=_parse_md5_length(payload.get("md5_length")),
        )
    )
