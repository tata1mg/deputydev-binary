from typing import List, Dict
from deputydev_core.models.dao.weaviate.urls_content import UrlsContent
from deputydev_core.services.repository.base_weaviate_repository import (
    BaseWeaviateRepository,
)
from deputydev_core.services.repository.dataclasses.main import (
    WeaviateSyncAndAsyncClients,
)
from weaviate.collections.classes.filters import Filter
from app.models.dtos.collection_dtos.urls_content_dto import UrlsContentDto
from weaviate.util import generate_uuid5
import asyncio
from datetime import datetime, timezone


class UrlsContentRepository(BaseWeaviateRepository):
    def __init__(self, weaviate_client: WeaviateSyncAndAsyncClients):
        super().__init__(weaviate_client, UrlsContent.collection_name)

    async def fetch_urls_objects(self, urls: List[str]) -> Dict[str, UrlsContentDto]:
        await self.ensure_collection_connections()
        filters = Filter.any_of(
            filters=[
                Filter.by_property("url").equal(url) for url in urls
            ]
        )
        obj = await self.async_collection.query.fetch_objects(
            filters=filters
        )
        if not obj.objects:
            return {}
        results = {
            item.properties["url"]: UrlsContentDto(**item.properties, id=str(item.uuid))
            for item in obj.objects
            if "url" in item.properties
        }
        return results

    def _prepare_properties(self, payload: UrlsContentDto) -> dict:
        payload.last_indexed = datetime.now().replace(tzinfo=timezone.utc)
        return payload.model_dump(mode="json", exclude={"id"})

    async def save_url_content(self, payload: UrlsContentDto):
        # backend_id is the id of url saved in backend postgres db
        existing = await self.fetch_urls_objects([payload.url])
        if existing and existing.get(payload.url):
            obj_id = existing[payload.url].id
            properties = self._prepare_properties(existing.get(payload.url))
            properties["name"] = payload.name
            await self.async_collection.data.update(uuid=obj_id, properties=properties)
        else:
            obj_id = generate_uuid5(payload.url)
            properties = self._prepare_properties(payload)
            await self.async_collection.data.insert(uuid=obj_id, properties=properties)

    async def bulk_update(self, payloads: List[UrlsContentDto]):
        # NOTE: bulk update is not supported in weaviate we have to update records one by one,
        # so do not use this function to update more than 10 records.
        if len(payloads) > 10:
            raise ValueError("This function is not optimized for updating more than 10 records")
        update_tasks = []
        for payload in payloads:
            properties = self._prepare_properties(payload)
            update_tasks.append(self.async_collection.data.update(uuid=payload.id, properties=properties))
        await asyncio.gather(*update_tasks)

    async def delete_url_content(self, url: str):
        await self.async_collection.data.delete_many(
            where=Filter.by_property("url").equal(url)
        )

    async def search_urls(self, keyword: str, limit=5):
        if len(keyword) < 3:
            content_filters = Filter.any_of(
                [
                    Filter.by_property("url").like(f"*{keyword}*"),
                    Filter.by_property("name").like(f"*{keyword}*")
                ]
            )
            results = await self.async_collection.query.fetch_objects(
                filters=content_filters,
                limit=limit,
            )
            return results
        else:
            results = await self.async_collection.query.bm25(
                query=keyword,
                query_properties=["url", "name"],
                return_properties=["url", "name", "last_indexed"],
                limit=limit
            )
            return results
