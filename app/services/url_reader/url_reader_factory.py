from app.services.url_reader.managers.public_url_reader_manager import PublicUrlReaderManager
from app.utils.constant.url_reader_constants import UrlReaderType


class UrlReaderFactory:
    url_readers = {UrlReaderType.PUBLIC_URL_READER: PublicUrlReaderManager}

    @classmethod
    def url_reader(cls, reader_type: UrlReaderType):
        return cls.url_readers[reader_type]
