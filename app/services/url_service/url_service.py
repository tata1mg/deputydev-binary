from app.clients.one_dev_client import OneDevClient
from app.services.url_service.url_manager_factory import UrlManagerFactory
from typing import TYPE_CHECKING
from app.repository.urls_content_repository import UrlsContentRepository
from deputydev_core.services.initialization.extension_initialisation_manager import (
    ExtensionInitialisationManager,
)
from app.utils.util import initialise_weaviate_client
from deputydev_core.utils.shared_memory import SharedMemory
from deputydev_core.utils.constants.enums import SharedMemoryKeys
from app.models.dtos.collection_dtos.urls_content_dto import UrlsContentDto
from datetime import datetime, timedelta, timezone
if TYPE_CHECKING:
    from app.models.dtos.url_dtos.url_reader_params import UrlReaderParams
    from app.models.dtos.url_dtos.save_url_params import SaveUrlParams
    from app.models.dtos.url_dtos.search_url_params import SearchUrlParams
    from app.models.dtos.url_dtos.list_url_params import ListUrlParams
    from app.models.dtos.url_dtos.update_url_params import UpdateUrlParams


class UrlService:
    async def fetch_urls_content(self, payload: "UrlReaderParams") -> dict:
        url_manager = UrlManagerFactory.url_manager(payload.url_type)()
        content = await url_manager.fetch_urls_content(payload)
        return content

    async def save_url(self, payload: "SaveUrlParams") -> dict:
        url_manager = UrlManagerFactory.url_manager(payload.url_type)()
        return await url_manager.save_url(payload)

    async def search_url(self, payload: "SearchUrlParams"):
        keyword = payload.keyword
        initialization_manager = ExtensionInitialisationManager()
        weaviate_client = await initialise_weaviate_client(initialization_manager)
        urls = await UrlsContentRepository(weaviate_client).search_urls(keyword, payload.limit)
        formatted_urls = [self.parse_url_model(url) for url in urls]
        return {"urls": formatted_urls}

    async def delete_url(self, url_id: int):
        await self.delete_url_from_backend(url_id)
        initialization_manager = ExtensionInitialisationManager()
        weaviate_client = await initialise_weaviate_client(initialization_manager)
        await UrlsContentRepository(weaviate_client).delete_url(url_id)

    async def delete_url_from_backend(self, url_id: int):
        headers = self.common_header()
        await OneDevClient().delete_url(headers, url_id)

    async def list_urls(self, payload: "ListUrlParams"):
        headers = self.common_header()
        urls_objects = await OneDevClient().list_urls(headers, payload.model_dump())
        return urls_objects

    async def update_url(self, payload: "UpdateUrlParams"):
        await self.update_url_in_backend(payload)
        initialization_manager = ExtensionInitialisationManager()
        weaviate_client = await initialise_weaviate_client(initialization_manager)
        url_obj = await UrlsContentRepository(weaviate_client).update_url(payload.url)
        parsed_url_model = self.parse_url_model(url_obj)
        return parsed_url_model

    async def update_url_in_backend(self, payload: "UpdateUrlParams") -> dict:
        headers = self.common_header()
        url_dict = await OneDevClient().update_url(headers, payload.url.model_dump())
        return url_dict

    @classmethod
    def common_header(cls):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SharedMemory.read(SharedMemoryKeys.EXTENSION_AUTH_TOKEN.value)}",
        }

    @classmethod
    def parse_url_model(cls, url_obj: UrlsContentDto, extra_fields=[]):
        default_fields = ["id", "name", "url", "last_indexed"]
        data = url_obj.model_dump(include=set(default_fields + extra_fields))
        data["id"] = url_obj.backend_id
        # data["last_indexed"] = data["last_indexed"].isoformat() if data["last_indexed"] else None
        if data["last_indexed"]:
            ist_offset = timedelta(hours=5, minutes=30)
            dt_ist = data["last_indexed"].astimezone(timezone(ist_offset))
            formatted_dt = dt_ist.strftime("%d/%m/%y %I:%M %p").lower()
            data["last_indexed"] = formatted_dt
        return data
