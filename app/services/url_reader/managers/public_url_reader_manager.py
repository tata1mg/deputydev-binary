import asyncio

from app.services.url_reader.managers.url_reader_manager import UrlReaderManager
from typing import List
from app.clients.web_client import WebClient
from app.services.url_reader.helpers.html_scrapper import HtmlScrapper


class PublicUrlReaderManager(UrlReaderManager):
    async def read_urls(self, urls: List[str]) -> dict:
        batch_size = 3
        tasks = []
        results = {}
        current_urls = []
        for url in urls:
            tasks.append(HtmlScrapper().scrape_markdown_from_url(url))
            current_urls.append(url)
            if len(tasks) == batch_size:
                urls_data = await asyncio.gather(*tasks)
                for index, fetched_url in enumerate(current_urls):
                    results[fetched_url] = urls_data[index]
                tasks = []
                current_urls = []
        if tasks:
            urls_data = await asyncio.gather(*tasks)
            for index, fetched_url in enumerate(current_urls):
                results[fetched_url] = urls_data[index]

        return results


