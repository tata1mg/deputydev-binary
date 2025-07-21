from functools import wraps
from typing import Any, Callable

from deputydev_core.services.mcp.dataclass.main import McpResponse, McpResponseMeta
from deputydev_core.utils.constants.enums import ContextValueKeys
from deputydev_core.utils.context_value import ContextValue
from deputydev_core.utils.context_vars import set_context_values
from sanic import Request

REQUIRED_HEADERS = ["X-Client", "X-Client-Version"]


def set_auth_token(headers: dict[str, str]) -> None:
    authorization_header = headers.get("Authorization")
    if authorization_header:
        auth_token = authorization_header.split(" ")[1]
        ContextValue.set(ContextValueKeys.EXTENSION_AUTH_TOKEN.value, auth_token)


def request_handler(func: Callable[[Request, Any, Any], Any]) -> Callable[[Request, Any, Any], Any]:
    """Decorator to store request headers in a context variable."""

    @wraps(func)
    async def wrapper(request: Request, *args: Any, **kwargs: Any) -> Callable[[Request, Any, Any], Any]:
        headers = request.headers
        required_headers = {header: headers.get(header) for header in REQUIRED_HEADERS}
        set_context_values(headers=required_headers)
        set_auth_token(headers)
        return await func(request, *args, **kwargs)

    return wrapper


def handle_mcp_exceptions(func: Callable[..., Any]) -> Callable[..., McpResponse]:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> McpResponse:
        try:
            result = await func(*args, **kwargs)
            return McpResponse(is_error=False, data=result)
        except Exception as ex:  # noqa: BLE001
            return McpResponse(is_error=True, meta=McpResponseMeta(message=str(ex)))

    return wrapper


def handle_ide_review_exceptions(func):
    """
    Decorator to handle exceptions in IDE review service.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return McpResponse(is_error=False, data=result)
        except Exception as ex:
            import traceback
            print(traceback.format_exc())
            return McpResponse(is_error=True, meta=McpResponseMeta(message=str(ex)))

    return wrapper