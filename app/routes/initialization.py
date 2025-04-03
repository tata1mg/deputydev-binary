import json

from deputydev_core.utils.app_logger import AppLogger
from sanic import Blueprint, HTTPResponse, Request

from app.services.initialization_service import InitializationService
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
        import traceback

        AppLogger.log_info(f"Error: {error}")
        AppLogger.log_info(f"Traceback: {traceback.format_exc()}")
        print(f"Error: {error}")
        print(f"Traceback: {traceback.format_exc()}")
        return HTTPResponse(
            body=json.dumps(
                {
                    "status": str(traceback.format_exc()),
                    "message": str(traceback.format_exc()),
                }
            )
        )
