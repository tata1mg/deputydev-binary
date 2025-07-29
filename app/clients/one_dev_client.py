from typing import Any, Dict

from deputydev_core.clients.http.adapters.http_response_adapter import (
    AiohttpToRequestsAdapter,
)
from deputydev_core.clients.http.base_http_client import BaseHTTPClient
from deputydev_core.utils.config_manager import ConfigManager
from deputydev_core.utils.constants.enums import ConfigConsumer

from app.utils.response_headers_handler import handle_client_response
from app.utils.util import get_common_headers


class OneDevClient(BaseHTTPClient):
    def __init__(self, config=None):
        if not config:
            self._host = ConfigManager.configs["DEPUTY_DEV"]["HOST"]
            timeout = ConfigManager.configs["DEPUTY_DEV"].get("TIMEOUT") or 60
            # The total number of simultaneous connections allowed (default is 100). (set 0 for unlimited)
            limit = ConfigManager.configs["DEPUTY_DEV"].get("LIMIT") or 0
            # The maximum number of connections allowed per host (default is 0, meaning unlimited).
            limit_per_host = ConfigManager.configs["DEPUTY_DEV"].get("LIMIT_PER_HOST") or 0
            # ttl_dns_cache: Time-to-live (TTL) for DNS cache entries, in seconds (default is 10).
            ttl_dns_cache = ConfigManager.configs["DEPUTY_DEV"].get("TTL_DNS_CACHE") or 10
        else:
            self._host = config["DEPUTY_DEV"]["HOST"]
            timeout = config["DEPUTY_DEV"].get("TIMEOUT") or 60
            limit = config["DEPUTY_DEV"].get("LIMIT") or 0
            limit_per_host = config["DEPUTY_DEV"].get("LIMIT_PER_HOST") or 0
            ttl_dns_cache = config["DEPUTY_DEV"].get("TTL_DNS_CACHE") or 10
        super().__init__(
            timeout=timeout,
            limit=limit,
            limit_per_host=limit_per_host,
            ttl_dns_cache=ttl_dns_cache,
        )

    @handle_client_response
    async def create_embedding(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        path = "/end_user/v1/code-gen/create-embedding"
        payload.update({"use_grace_period": ConfigManager.configs["USE_GRACE_PERIOD_FOR_EMBEDDING"]})
        headers = {**headers, **get_common_headers()}
        result = await self.post(url=self._host + path, json=payload, headers=headers)
        return result

    @handle_client_response
    async def llm_reranking(self, payload: Dict[str, Any], headers: Dict[str, str]):
        path = "/end_user/v1/chunks/rerank-via-llm"
        headers = {**headers, **get_common_headers()}
        result = await self.post(url=self._host + path, json=payload, headers=headers)
        return result

    @handle_client_response
    async def get_configs(self, headers: Dict[str, str]) -> AiohttpToRequestsAdapter:
        path = "/end_user/v1/configs/get-configs"
        headers = {**headers, **get_common_headers()}

        result = await self.get(
            url=self._host + path,
            headers=headers,
            params={"consumer": ConfigConsumer.BINARY.value},
        )
        return result

    @handle_client_response
    async def verify_auth_token(self, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify the authentication token for the user.

        Args:
            headers (Dict[str, str]): The headers containing the authentication token.

        Returns:
            Dict[str, Any]: A dictionary containing the verification result if successful, otherwise None.

        Raises:
            Exception: Raises an exception if the request fails or the response is not valid.
        """
        path = "/end_user/v1/auth/verify-auth-token"
        headers = {**headers, **get_common_headers()}
        result = await self.post(url=self._host + path, headers=headers, json=payload)
        return result

    @handle_client_response
    async def summarize_url_content(self, payload: dict, headers):
        path = "/end_user/v1/urls/summarize_url"
        headers = {"X-Session-Type": headers.get("X-Session-Type"), **get_common_headers(add_auth=True)}
        result = await self.post(url=self._host + path, headers=headers, json=payload)
        return result

    @handle_client_response
    async def save_url(self, payload: dict, headers: Dict[str, str] = {}):
        path = "/end_user/v1/urls/save_url"
        headers = {**headers, **get_common_headers(add_auth=True)}
        result = await self.post(url=self._host + path, headers=headers, json=payload)
        return result

    @handle_client_response
    async def delete_url(self, url_id: int, headers: Dict[str, str] = {}):
        path = "/end_user/v1/urls/delete_url"
        headers = {**headers, **get_common_headers(add_auth=True)}
        result = await self.get(
            url=self._host + path,
            headers=headers,
            params={"url_id": str(url_id)},
        )
        return result

    @handle_client_response
    async def list_urls(self, params: dict, headers: Dict[str, str] = {}):
        path = "/end_user/v1/urls/saved_url/list"
        headers = {**headers, **get_common_headers(add_auth=True)}
        result = await self.get(
            url=self._host + path,
            headers=headers,
            params=params,
        )
        return result

    @handle_client_response
    async def update_url(self, payload, headers: Dict[str, str] = {}):
        path = "/end_user/v1/urls/update_url"
        headers = {**headers, **get_common_headers(add_auth=True)}
        result = await self.put(url=self._host + path, headers=headers, json=payload)
        return result
