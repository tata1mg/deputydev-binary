from functools import wraps

from deputydev_core.utils.constants.enums import SharedMemoryKeys
from deputydev_core.utils.context_vars import set_context_values
from deputydev_core.utils.shared_memory import SharedMemory
from sanic import Request

REQUIRED_HEADERS = ["X-Client", "X-Client-Version"]


def set_auth_token(headers):
    authorization_header = headers.get("Authorization")
    if authorization_header:
        auth_token = authorization_header.split(" ")[1]
        SharedMemory.create(SharedMemoryKeys.EXTENSION_AUTH_TOKEN.value, auth_token)


def request_handler(func):
    """Decorator to store request headers in a context variable."""

    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        headers = request.headers
        required_headers = {header: headers.get(header) for header in REQUIRED_HEADERS}
        set_context_values(headers=required_headers)
        set_auth_token(headers)
        return await func(request, *args, **kwargs)

    return wrapper
