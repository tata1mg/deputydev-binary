from typing import Any, Dict, Optional
from deputydev_core.clients.http.base_http_client import BaseHTTPClient
from deputydev_core.utils.constants.enums import ConfigConsumer


class OneDevClient(BaseHTTPClient):
    def __init__(self, config=None):
        from deputydev_core.utils.config_manager import ConfigManager

        print(ConfigManager.configs)
        config = {
            "DEPUTY_DEV": {
                "HOST": "http://localhost:8084",
                "TIMEOUT": 15,
                "LIMIT": 0,
                "LIMIT_PER_HOST": 0,
                "TTL_DNS_CACHE": 10,
            }
        }
        if not config:
            self._host = ConfigManager.configs["DEPUTY_DEV"]["HOST"]
            timeout = ConfigManager.configs["DEPUTY_DEV"].get("TIMEOUT") or 15
            # The total number of simultaneous connections allowed (default is 100). (set 0 for unlimited)
            limit = ConfigManager.configs["DEPUTY_DEV"].get("LIMIT") or 0
            # The maximum number of connections allowed per host (default is 0, meaning unlimited).
            limit_per_host = (
                ConfigManager.configs["DEPUTY_DEV"].get("LIMIT_PER_HOST") or 0
            )
            # ttl_dns_cache: Time-to-live (TTL) for DNS cache entries, in seconds (default is 10).
            ttl_dns_cache = (
                ConfigManager.configs["DEPUTY_DEV"].get("TTL_DNS_CACHE") or 10
            )
        else:
            self._host = config["DEPUTY_DEV"]["HOST"]
            timeout = config["DEPUTY_DEV"].get("TIMEOUT") or 15
            limit = config["DEPUTY_DEV"].get("LIMIT")
            limit_per_host = config["DEPUTY_DEV"].get("LIMIT_PER_HOST")
            ttl_dns_cache = config["DEPUTY_DEV"].get("TTL_DNS_CACHE")
        super().__init__(
            timeout=timeout,
            limit=limit,
            limit_per_host=limit_per_host,
            ttl_dns_cache=ttl_dns_cache,
        )

    async def create_embedding(
        self, payload: Dict[str, Any], headers: Dict[str, str]
    ) -> Dict[str, Any]:
        path = "/end_user/v1/code-gen/create-embedding"
        headers = {**headers, "X-Client": "VSCODE_EXT", "X-Client-Version": "2.0.0"}
        result = await self.post(url=self._host + path, json=payload, headers=headers)
        return (await result.json()).get("data")

    async def llm_reranking(self, payload: Dict[str, Any], headers: Dict[str, str]):
        path = "/end_user/v1/chunks/rerank-via-llm"
        headers = {**headers, "X-Client": "VSCODE_EXT", "X-Client-Version": "2.0.0"}
        result = await self.post(url=self._host + path, json=payload, headers=headers)
        return (await result.json()).get("data")

    async def get_configs(self, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        path = "/end_user/v1/configs/get-configs"
        headers = {**headers, "X-Client": "BINARY", "X-Client-Version": "1.0.0"}
        result = await self.get(
            url=self._host + path,
            headers=headers,
        )
        return (await result.json()).get("data")
