from bs4 import BeautifulSoup
import html2text
from app.clients.web_client import WebClient
from urllib.parse import urlparse
from typing import Tuple
import hashlib
from requests.structures import CaseInsensitiveDict
from app.models.dtos.collection_dtos.urls_content_dto import UrlsContentDto, CacheHeaders


class HtmlScrapper:
    def __init__(self, timeout: int = 10):
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.web_client = WebClient()

    async def fetch_html(self, url: str, headers=None) -> Tuple[str, CaseInsensitiveDict, str]:
        if headers is None:
            headers = {}
        content, response_headers, status = await self.web_client.get_content(url, headers.update(self.headers))
        response_headers = CaseInsensitiveDict(response_headers)
        return content, response_headers, status

    def clean_html(self, raw_html: str, url: str) -> BeautifulSoup:
        soup = BeautifulSoup(raw_html, "html.parser")
        return soup

    def convert_html_to_markdown(self, cleaned_html: str) -> str:
        return html2text.html2text(cleaned_html)

    def extract_fragment(self, soup: BeautifulSoup, fragment: str) -> str:
        target = soup.find(id=fragment)
        return str(target) if target else str(soup)  # fallback to full content if not found

    @staticmethod
    def string_to_hash(input_string: str) -> str:
        # Convert the string to bytes, then hash it
        return hashlib.sha256(input_string.encode('utf-8')).hexdigest()

    async def scrape_markdown_from_url(self, url: str, is_content_cached: bool = False,
                                       existing_content: "UrlsContentDto" = None) -> Tuple[str, bool]:
        parsed = urlparse(url)
        base_url = parsed._replace(fragment="").geturl()
        fragment_id = parsed.fragment
        headers = self.get_conditional_headers(existing_content) if is_content_cached else {}
        is_cached_content_matched = False

        raw_html, response_headers, status = await self.fetch_html(base_url, headers)

        content_hash = self.string_to_hash(raw_html)
        if is_content_cached and existing_content:
            if self.should_use_cached_content(status, existing_content, content_hash):
                is_cached_content_matched = True
                return existing_content.content, is_cached_content_matched
            if status == 200:
                self.update_cache_metadata(existing_content, response_headers, content_hash)

        soup = self.clean_html(raw_html, url)
        target_html = self.extract_fragment(soup, fragment_id) if fragment_id else str(soup)
        markdown = self.convert_html_to_markdown(target_html)
        return markdown, is_cached_content_matched

    def get_conditional_headers(self, existing_content: "UrlsContentDto") -> dict:
        headers = {}
        if existing_content.cache_headers:
            if existing_content.cache_headers.etag:
                headers["If-None-Match"] = existing_content.cache_headers.etag
            if existing_content.cache_headers.last_modified:
                headers["If-Modified-Since"] = existing_content.cache_headers.last_modified
        return headers

    def should_use_cached_content(self, status: str, existing_content: "UrlsContentDto", content_hash: str) -> bool:
        if status == 304:
            return True
        if status == 200:
            return existing_content.content_hash == content_hash
        return False

    def update_cache_metadata(self, existing_content: "UrlsContentDto", response_headers: CaseInsensitiveDict,
                              content_hash: str):
        etag = response_headers.get("ETag")
        last_modified = response_headers.get("Last-Modified")
        cache_control = response_headers.get("Cache-Control", "").lower()
        headers_resp = {}
        if cache_control and "no-store" not in cache_control:
            if etag:
                headers_resp["etag"] = etag
            if last_modified:
                headers_resp["last_modified"] = last_modified
            if headers_resp:
                existing_content.cache_headers = CacheHeaders(**headers_resp)
        existing_content.content_hash = content_hash
