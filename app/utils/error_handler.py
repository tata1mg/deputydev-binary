import json
import traceback

from sanic.exceptions import BadRequest, ServerError
from sanic.response import HTTPResponse


def error_handler(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ServerError as se:
            print(traceback.format_exc())
            error_response = {
                "error_code": 500,
                "error_type": "SERVER_ERROR",
                "error_message": str(se),
                "traceback": str(traceback.format_exc()),
            }
            return HTTPResponse(body=json.dumps(error_response), status=500)
        except BadRequest as be:
            print(traceback.format_exc())
            if str(be) == "INVALID_PARAMS":
                error_response = {
                    "error_code": 400,
                    "error_type": "INVALID_PARAMS",
                    "error_message": "Request failed due to invalid parameters",
                    "traceback": str(traceback.format_exc()),
                }
                return HTTPResponse(body=json.dumps(error_response), status=400)
            error_response = {
                "error_code": 400,
                "error_type": "BAD_REQUEST",
                "error_message": str(be),
                "traceback": str(traceback.format_exc()),
            }
            return HTTPResponse(body=json.dumps(error_response), status=400)
        except ValueError as ve:
            print(traceback.format_exc())
            error_response = {
                "error_code": 400,
                "error_type": "VALUE_ERROR",
                "error_message": str(ve),
                "traceback": str(traceback.format_exc()),
            }
            return HTTPResponse(body=json.dumps(error_response), status=400)
        except Exception as e:
            print(traceback.format_exc())
            error_response = {
                "error_code": 500,
                "error_type": "SERVER_ERROR",
                "error_message": str(e),
                "traceback": str(traceback.format_exc()),
            }
            return HTTPResponse(body=json.dumps(error_response), status=500)

    return wrapper
