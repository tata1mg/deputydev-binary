from app.services.url_service.url_manager_factory import UrlManagerFactory
from typing import TYPE_CHECKING
from app.repository.urls_content_repository import UrlsContentRepository
from deputydev_core.services.initialization.extension_initialisation_manager import (
    ExtensionInitialisationManager,
)
from app.utils.util import initialise_weaviate_client

if TYPE_CHECKING:
    from app.models.dtos.url_dtos.url_reader_params import UrlReaderParams
    from app.models.dtos.url_dtos.save_url_params import SaveUrlParams
    from app.models.dtos.url_dtos.search_url_params import SearchUrlParams


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
        return urls

    # async def delete_url(self, ):