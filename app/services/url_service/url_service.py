from app.clients.one_dev_client import OneDevClient
from app.services.url_service.url_manager_factory import UrlManagerFactory
from typing import TYPE_CHECKING
from app.repository.urls_content_repository import UrlsContentRepository
from deputydev_core.services.initialization.extension_initialisation_manager import (
    ExtensionInitialisationManager,
)
from deputydev_core.utils.weaviate import get_weaviate_client
from app.services.url_service.helpers.url_serializer import UrlSerializer
from app.models.dtos.collection_dtos.urls_content_dto import UrlsContentDto

if TYPE_CHECKING:
    from app.models.dtos.url_dtos.url_reader_params import UrlReaderParams
    from app.models.dtos.url_dtos.save_url_params import SaveUrlParams
    from app.models.dtos.url_dtos.search_url_params import SearchUrlParams
    from app.models.dtos.url_dtos.list_url_params import ListUrlParams
    from app.models.dtos.url_dtos.update_url_params import UpdateUrlParams


class UrlService:
    async def get_weaviate_client(self):
        initialization_manager = ExtensionInitialisationManager()
        weaviate_client = await get_weaviate_client(initialization_manager)
        return weaviate_client

    async def fetch_urls_content(self, payload: "UrlReaderParams") -> dict:
        url_manager = UrlManagerFactory.url_manager(payload.url_type)()
        content = await url_manager.fetch_urls_content(payload)
        return content

    async def save_url(self, payload: "SaveUrlParams") -> dict:
        url_manager = UrlManagerFactory.url_manager(payload.url_type)()
        return await url_manager.save_url(payload)

    async def search_url(self, payload: "SearchUrlParams"):
        keyword = payload.keyword
        weaviate_client = await self.get_weaviate_client()
        urls = await UrlsContentRepository(weaviate_client).search_urls(keyword, payload.limit)
        formatted_urls = [UrlSerializer.parse_url_model(url) for url in urls]
        return {"urls": formatted_urls}

    async def delete_url(self, url_id: int):
        await self.delete_url_from_backend(url_id)
        weaviate_client = await self.get_weaviate_client()
        await UrlsContentRepository(weaviate_client).delete_url(url_id)

    async def delete_url_from_backend(self, url_id: int):
        await OneDevClient().delete_url(url_id)

    async def list_urls(self, payload: "ListUrlParams"):
        urls_objects = await OneDevClient().list_urls(payload.model_dump())
        return urls_objects if urls_objects else []

    async def update_url(self, payload: "UpdateUrlParams"):
        await self.update_url_in_backend(payload)
        weaviate_client = await self.get_weaviate_client()
        url_obj = await UrlsContentRepository(weaviate_client).update_url(payload.url)
        parsed_url_model = UrlSerializer.parse_url_model(url_obj)
        return parsed_url_model

    async def update_url_in_backend(self, payload: "UpdateUrlParams") -> dict:
        url_dict = await OneDevClient().update_url(payload.url.model_dump())
        return url_dict

    async def refill_urls_data(self):
        limit = 60
        offset = 0
        all_url_objects = []
        weaviate_client = await self.get_weaviate_client()
        while True:
            urls_data = await OneDevClient().list_urls(params={"limit": limit, "offset": offset})
            url_dicts = urls_data["urls"]
            if not url_dicts:
                break  # no more data

            for url in url_dicts:
                url["backend_id"] = url.pop("id")
                all_url_objects.append(UrlsContentDto(**url))
            if all_url_objects:
                await UrlsContentRepository(weaviate_client).bulk_insert(all_url_objects)
            meta = urls_data.get("meta", {})
            total_count = meta.get("total_count", 0)
            offset += limit
            if offset >= total_count:
                break
