from sanic import Blueprint, Request, json
from app.services.initialization_service import InitializationService
from sanic import HTTPResponse
import json

initialization = Blueprint("initialization", url_prefix="")


@initialization.route("/init", methods=["POST"])
async def initialize_service(_request: Request, **kwargs):
    try:
        headers = _request.headers
        payload = _request.json
        authorization_header = headers.get("Authorization")
        auth_token = authorization_header.split(" ")[1]
        await InitializationService.initialization(auth_token=auth_token, payload=payload)
        return HTTPResponse(body=json.dumps({"status": "Completed"}))
    except Exception as error:
        return HTTPResponse(body=json.dumps({"status": "Failed"}))
