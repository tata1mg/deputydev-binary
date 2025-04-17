from bs4 import BeautifulSoup
import html2text
from app.clients.web_client import WebClient
from urllib.parse import urlparse


class HtmlScrapper:
    def __init__(self, timeout: int = 10):
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.web_client = WebClient()

    async def fetch_html(self, url: str) -> str:
        content = await self.web_client.get_content(url, self.headers)
        return content

    def clean_html(self, raw_html: str, url: str) -> BeautifulSoup:
        soup = BeautifulSoup(raw_html, "html.parser")
        # for tag in soup(["script", "style", "noscript", "iframe"]):
        #     tag.decompose()
        return soup

    def convert_html_to_markdown(self, cleaned_html: str) -> str:
        return html2text.html2text(cleaned_html)

    def extract_fragment(self, soup: BeautifulSoup, fragment: str) -> str:
        target = soup.find(id=fragment)
        return str(target) if target else str(soup)  # fallback to full content if not found

    async def scrape_markdown_from_url(self, url: str) -> str:
        parsed = urlparse(url)
        base_url = parsed._replace(fragment="").geturl()
        fragment_id = parsed.fragment
        raw_html = await self.fetch_html(base_url)
        soup = self.clean_html(raw_html, url)
        if fragment_id:
            target_html = self.extract_fragment(soup, fragment_id)
        else:
            target_html = str(soup)
        markdown = self.convert_html_to_markdown(target_html)
        return markdown
