from app.services.url_service.url_manager_factory import UrlManagerFactory
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.dtos.url_dtos.url_reader_params import UrlReaderParams
    from app.models.dtos.url_dtos.save_url_params import SaveUrlParams


class UrlService:
    async def fetch_urls_content(self, payload: "UrlReaderParams") -> dict:
        url_manager = UrlManagerFactory.url_manager(payload.url_type)()
        content = await url_manager.fetch_urls_content(payload.urls)
        return content

    async def save_url(self, payload: "SaveUrlParams"):
        url_manager = UrlManagerFactory.url_manager(payload.url_type)()
        await url_manager.save_url(payload)
