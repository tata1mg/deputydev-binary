import json
import traceback
from collections.abc import Awaitable
from typing import Any, Callable, Dict, List, Optional, Type

from sanic.exceptions import BadRequest
from sanic.response import HTTPResponse

from app.utils.route_error_handler.error_type_handlers.base_error_type_handler import BaseErrorTypeHandler


def _handle_errors_from_handlers(
    handlers: List[Type[BaseErrorTypeHandler]], error: Exception
) -> Optional[HTTPResponse]:
    """Handle the error using the provided list of error handlers.   If a handler returns a response, it will be returned; otherwise, None is returned."""
    for handler in handlers:
        handler_response = handler.handle_error(error)
        if handler_response is not None:
            return handler_response
    return None


def _handle_fallback_error(error: Exception) -> HTTPResponse:
    """Handle fallback errors that are not caught by specific handlers."""
    # Fallback error handling
    if isinstance(error, BadRequest):
        error_response: Dict[str, Optional[str]] = {
            "error_code": "400",
            "error_type": "BAD_REQUEST",
            "error_subtype": None,
            "error_message": str(error),
            "traceback": str(traceback.format_exc()),
        }
        return HTTPResponse(body=json.dumps(error_response), status=400)

    elif isinstance(error, ValueError):
        error_response: Dict[str, Optional[str]] = {
            "error_code": "400",
            "error_type": "VALUE_ERROR",
            "error_subtype": None,
            "error_message": str(error),
            "traceback": str(traceback.format_exc()),
        }
        return HTTPResponse(body=json.dumps(error_response), status=400)

    # Handle any other exceptions
    else:
        error_response: Dict[str, Optional[str]] = {
            "error_code": "500",
            "error_type": "SERVER_ERROR",
            "error_subtype": None,
            "error_message": str(error),
            "traceback": str(traceback.format_exc()),
        }
        return HTTPResponse(body=json.dumps(error_response), status=500)


def _error_handler(
    func: Callable[..., Awaitable[HTTPResponse]], special_handlers: List[Type[BaseErrorTypeHandler]] = []
) -> Callable[..., Awaitable[HTTPResponse]]:
    async def wrapper(*args: Any, **kwargs: Any) -> HTTPResponse:
        try:
            return await func(*args, **kwargs)
        except Exception as _ex:  # noqa: BLE001
            handler_response = _handle_errors_from_handlers(special_handlers, _ex)
            if handler_response is not None:
                return handler_response

            return _handle_fallback_error(_ex)

    return wrapper


def get_error_handler(
    special_handlers: List[Type[BaseErrorTypeHandler]] = [],
) -> Callable[..., Callable[..., Awaitable[HTTPResponse]]]:
    """
    Returns a decorator that wraps the route handler with error handling logic.
    It will use the provided special handlers to handle specific errors.
    If no special handlers are provided, it will use a fallback error handler.
    """

    def decorator(func: Callable[..., Awaitable[HTTPResponse]]) -> Callable[..., Awaitable[HTTPResponse]]:
        return _error_handler(func, special_handlers)

    return decorator
