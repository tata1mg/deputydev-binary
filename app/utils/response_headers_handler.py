from functools import wraps
from typing import Any, Awaitable, Callable, Dict, Optional

from deputydev_core.clients.http.adapters.http_response_adapter import (
    AiohttpToRequestsAdapter,
)
from deputydev_core.services.auth_token_storage.auth_token_service import (
    AuthTokenService,
)
from deputydev_core.utils.app_logger import AppLogger
from deputydev_core.utils.constants.enums import SharedMemoryKeys
from deputydev_core.utils.context_vars import get_context_value
from deputydev_core.utils.shared_memory import SharedMemory

from app.utils.constants import Headers


def handle_client_response(func: Callable[..., Awaitable[AiohttpToRequestsAdapter]]) -> Callable[..., Awaitable[Any]]:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Optional[Dict[str, Any]]:
        result = await func(*args, **kwargs)
        response_headers = result.headers
        auth_token = response_headers.get("new_session_data")
        if auth_token:
            SharedMemory.create(SharedMemoryKeys.EXTENSION_AUTH_TOKEN.value, auth_token)
            await AuthTokenService.store_token(get_context_value("headers").get(Headers.X_CLIENT))
        result = await result.json()

        if "data" in result:
            return result["data"]
        else:
            AppLogger.log_error(
                f"Error in response: {result}",
            )
            return None

    return wrapper
