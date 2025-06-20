import asyncio
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, List

from deputydev_core.services.initialization.extension_initialisation_manager import (
    ExtensionInitialisationManager,
)
from deputydev_core.utils.config_manager import ConfigManager
from deputydev_core.utils.weaviate import get_weaviate_client

from app.clients.one_dev_client import OneDevClient
from app.models.dtos.collection_dtos.urls_content_dto import UrlsContentDto
from app.repository.urls_content_repository import UrlsContentRepository
from app.services.url_service.helpers.html_scrapper import HtmlScrapper
from app.services.url_service.helpers.url_serializer import UrlSerializer
from app.services.url_service.managers.url_manager import UrlManager

if TYPE_CHECKING:
    from app.models.dtos.url_dtos.save_url_params import SaveUrlParams
    from app.models.dtos.url_dtos.url_reader_params import UrlReaderParams


class PublicUrlManager(UrlManager):
    BACKEND_FIELDS = ["name", "url", "last_indexed"]

    def __init__(self):
        self.batch_size = ConfigManager.configs["URL_CONTENT_READER"]["BATCH_SIZE"]
        self.validate_content_updation = ConfigManager.configs["URL_CONTENT_READER"]["VALIDATE_CONTENT_UPDATION"]
        self.max_content_size = ConfigManager.configs["URL_CONTENT_READER"]["MAX_CONTENT_SIZE"]
        self.summarize_large_content = ConfigManager.configs["URL_CONTENT_READER"]["SUMMARIZE_LARGE_CONTENT"]

    async def _read_urls(self, urls: List[str]) -> Dict[str, UrlsContentDto]:
        """
        Asynchronously read and process a list of URLs, fetching their content and managing caching.

        This method performs the following tasks:
        1. Initializes a Weaviate client for database operations.
        2. Fetches existing content for the given URLs from the database.
        3. Processes URLs in batches, scraping content when necessary.
        4. Handles content validation and updating based on the `validate_content_updation` flag.
        5. Updates the database if content of existing urls updated.

        Args:
            urls (List[str]): A list of URLs to process.

        Returns:
            Dict[str, UrlsContentDto]: A dictionary mapping URLs to their corresponding UrlsContentDto objects.

        Notes:
            - The method uses batching (controlled by `self.batch_size`) to process URLs efficiently.
            - It respects the `validate_content_updation` flag to determine whether to re-scrape existing content.
            - The method creates an asynchronous task to update the database with modified content.

        Raises:
            Any exceptions raised by the underlying services (e.g., HtmlScrapper, UrlsContentRepository)
            will be propagated.
        """
        tasks = []
        results = {}
        current_urls = []
        updated_objects: List[UrlsContentDto] = []
        initialization_manager = ExtensionInitialisationManager()
        weaviate_client = await get_weaviate_client(initialization_manager)
        existing_contents = await UrlsContentRepository(weaviate_client).fetch_urls_objects(urls)

        for url in urls:
            if not self.validate_content_updation and url in existing_contents and existing_contents[url].content:
                # If content updation is not need to be checked and urls content is already present in db then:
                results[url] = existing_contents[url]
                continue
            if self.validate_content_updation and url in existing_contents and existing_contents[url].content:
                tasks.append(
                    HtmlScrapper().scrape_markdown_from_url(
                        url, existing_content=existing_contents[url], is_content_cached=True
                    )
                )
            else:
                tasks.append(HtmlScrapper().scrape_markdown_from_url(url))
            current_urls.append(url)
            if len(tasks) == self.batch_size:
                results.update(await self._gather_batch(tasks, current_urls, existing_contents, updated_objects))
                tasks, current_urls = [], []
        if tasks:
            results.update(await self._gather_batch(tasks, current_urls, existing_contents, updated_objects))
        # update objects that are in db and content is updated.
        asyncio.create_task(UrlsContentRepository(weaviate_client).bulk_update(updated_objects))
        return results

    async def fetch_urls_content(self, payload: "UrlReaderParams") -> dict:
        urls = payload.urls
        results = await self._read_urls(urls)
        url_contents = {url: obj.content for url, obj in results.items()}
        formatted_content = self._format_urls_content(url_contents)
        if len(formatted_content) > self.max_content_size and self.summarize_large_content:
            summarized_content = await self._summarize_content(formatted_content, payload)
            return {"content": summarized_content}
        else:
            return {"content": formatted_content}

    async def _summarize_content(self, content, payload):
        headers = {}
        if payload.session_id:
            headers["X-Session-Id"] = str(payload.session_id)
        if payload.session_type:
            headers["X-Session-Type"] = payload.session_type
        payload = {"content": content}
        summarize_content = await OneDevClient().summarize_url_content(payload, headers)
        return summarize_content

    def _format_urls_content(self, url_contents: Dict[str, str]) -> str:
        formatted_content = ""
        for url, content in url_contents.items():
            formatted_content += f"Content of URL {url}: \n {content} \n\n"
        return formatted_content

    @classmethod
    def _last_indexed(cls):
        return datetime.now(timezone.utc)

    async def save_url(self, payload: "SaveUrlParams") -> dict:
        last_indexed = self._last_indexed()
        url = UrlsContentDto(name=payload.url.name, url=payload.url.url, last_indexed=last_indexed)
        url_data = await self._save_url_in_backend(url)
        initialization_manager = ExtensionInitialisationManager()
        weaviate_client = await get_weaviate_client(initialization_manager)
        url.backend_id = url_data["id"]
        await UrlsContentRepository(weaviate_client).save_url_content(url)
        asyncio.create_task(self._save_url_content(url, weaviate_client))
        return UrlSerializer.parse_url_model(url)

    async def _save_url_content(self, url_content: UrlsContentDto, weaviate_client):
        # If user is creating a different record for already saved url with different name
        # or same name
        results = await self._read_urls([url_content.url])
        content: UrlsContentDto = results.get(url_content.url)
        if content:
            await UrlsContentRepository(weaviate_client).save_url_content(content)
            print("Successfully Updated Content")

    async def _gather_batch(
        self, tasks, urls: List[str], existing_contents: Dict[str, UrlsContentDto], updated_urls: List[UrlsContentDto]
    ):
        results = {}
        urls_data = await asyncio.gather(*tasks)
        for index, fetched_url in enumerate(urls):
            if fetched_url in existing_contents:
                results[fetched_url] = existing_contents[fetched_url]
                results[fetched_url].content = urls_data[index][0]
            else:
                results[fetched_url] = UrlsContentDto(content=urls_data[index][0], url=fetched_url)
            is_saved_content_matched = urls_data[index][1]
            if not is_saved_content_matched and fetched_url in existing_contents:
                updated_urls.append(existing_contents[fetched_url])
        return results

    async def _save_url_in_backend(self, payload: "UrlsContentDto") -> dict:
        data = payload.model_dump(include=set(self.BACKEND_FIELDS))
        data["last_indexed"] = data["last_indexed"].isoformat() if data["last_indexed"] else None
        url = await OneDevClient().save_url(data)
        return url
