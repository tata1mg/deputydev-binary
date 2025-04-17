from app.services.url_reader.url_reader_factory import UrlReaderFactory
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.dtos.url_reader_params import UrlReaderParams


class UrlReaderService:
    async def read_urls(self, payload: "UrlReaderParams") -> dict:
        url_reader = UrlReaderFactory.url_reader(payload.url_type)()
        content = await url_reader.read_urls(payload.urls)
        return content
