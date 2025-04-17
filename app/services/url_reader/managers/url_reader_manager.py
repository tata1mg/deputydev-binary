from abc import ABC


class UrlReaderManager(ABC):
    async def read_urls(self, payload):
        raise NotImplementedError
