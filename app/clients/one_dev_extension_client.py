from typing import Any, Dict, Optional

from deputydev_core.clients.http.service_clients.one_dev_client import OneDevClient


class OneDevExtensionClient(OneDevClient):
    async def create_embedding(
        self, payload: Dict[str, Any], headers: Dict[str, str]
    ) -> Dict[str, Any]:
        path = "/end_user/v1/create-embedding"
        result = await self.post(url=self._host + path, json=payload, headers=headers)
        return (await result.json()).get("data")

    async def llm_reranking(self, payload: Dict[str, Any], headers: Dict[str, str]):
        path = "/end_user/v1/llm_reranking"
        result = await self.post(url=self._host + path, json=payload, headers=headers)
        return (await result.json()).get("data")

    async def get_configs(self, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        path = "/end_user/v1/get-configs"
        result = await self.get(url=self._host + path, headers=headers)
        return (await result.json()).get("data")
