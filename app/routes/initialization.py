from sanic import Blueprint, Request, json
from app.services.initialization_service import InitializationService
from sanic import HTTPResponse
import json

from app.utils.request_handlers import request_handler

initialization = Blueprint("initialization", url_prefix="")


@initialization.route("/init", methods=["POST"])
@request_handler
async def initialize_service(_request: Request, **kwargs):
    try:
        payload = _request.json
        await InitializationService.initialization(payload=payload)
        return HTTPResponse(body=json.dumps({"status": "Completed"}))
    except Exception as error:
        return HTTPResponse(body=json.dumps({"status": "Failed"}))
