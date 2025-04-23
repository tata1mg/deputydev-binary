from typing import Any, Dict

from deputydev_core.clients.http.adapters.http_response_adapter import (
    AiohttpToRequestsAdapter,
)
from deputydev_core.clients.http.base_http_client import BaseHTTPClient
from deputydev_core.utils.config_manager import ConfigManager
from deputydev_core.utils.constants.enums import ConfigConsumer

from app.utils.response_headers_handler import handle_client_response
from app.utils.util import get_common_headers


class WebClient(BaseHTTPClient):
    def __init__(self, config=None):
        timeout = 60
        limit = 0
        limit_per_host = 0
        ttl_dns_cache = 10
        super().__init__(
            timeout=timeout,
            limit=limit,
            limit_per_host=limit_per_host,
            ttl_dns_cache=ttl_dns_cache,
        )

    async def get_content(self, url, headers):
        content = await self.get(url, headers=headers)
        content_text, response_headers, status_code = content.text, content.headers, content.status_code
        return content_text, response_headers, status_code
