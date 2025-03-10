from typing import Any, Dict, Optional

from deputydev_core.clients.http.service_clients.one_dev_client import OneDevClient

from app.utils.constants import DEPUTYDEV_HOST


class OneDevExtensionClient(OneDevClient):
    async def create_embedding(
        self, payload: Dict[str, Any], headers: Dict[str, str]
    ) -> Dict[str, Any]:
        host = DEPUTYDEV_HOST
        path = "/end_user/v1/code-gen/create-embedding"
        headers = {**headers, "X-Client": "VSCODE_EXT", "X-Client-Version": "2.0.0"}
        result = await self.post(url=host + path, json=payload, headers=headers)
        return (await result.json()).get("data")

    async def llm_reranking(self, payload: Dict[str, Any], headers: Dict[str, str]):
        path = "/end_user/v1/chunks/rerank-via-llm"
        headers = {**headers, "X-Client": "VSCODE_EXT", "X-Client-Version": "2.0.0"}
        result = await self.post(url=self._host + path, json=payload, headers=headers)
        return (await result.json()).get("data")

    async def get_configs(self, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        path = "/end_user/v1/get-configs"
        headers = {**headers, "X-Client": "VSCODE_EXT", "X-Client-Version": "2.0.0"}
        result = await self.get(url=self._host + path, headers=headers)
        return (await result.json()).get("data")
