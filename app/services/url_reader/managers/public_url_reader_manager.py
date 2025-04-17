from app.services.url_reader.managers.url_reader_manager import UrlReaderManager
from typing import List
from app.clients.web_client import WebClient
from app.services.url_reader.helpers.html_scrapper import HtmlScrapper


class PublicUrlReaderManager(UrlReaderManager):
    async def read_urls(self, urls: List[str]) -> dict:
        batch_size = 3
        tasks = []
        result = {}
        for url in urls:
            content = await HtmlScrapper().scrape_markdown_from_url(url)
            result[url] = content
        return result


