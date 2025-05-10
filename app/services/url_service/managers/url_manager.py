from abc import ABC


class UrlManager(ABC):
    async def fetch_urls_content(self, payload):
        raise NotImplementedError

    async def save_url(self, payload):
        raise NotImplementedError
