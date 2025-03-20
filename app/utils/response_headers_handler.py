from functools import wraps
from typing import Callable, Dict, Any, Optional, Awaitable
from deputydev_core.utils.shared_memory import SharedMemory
from deputydev_core.utils.constants.enums import SharedMemoryKeys
from deputydev_core.clients.http.adapters.http_response_adapter import AiohttpToRequestsAdapter


def handle_client_response(func: Callable[..., Awaitable[AiohttpToRequestsAdapter]]) -> Callable[..., Awaitable[Any]]:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Optional[Dict[str, Any]]:
        result = await func(*args, **kwargs)
        response_headers = result.headers
        auth_token = response_headers.get("new_session_data")
        if auth_token:
            SharedMemory.create(SharedMemoryKeys.EXTENSION_AUTH_TOKEN.value, auth_token)
        result = await result.json()
        return result.get("data")

    return wrapper
