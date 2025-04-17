from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.utils.constant.url_reader_constants import UrlReaderType


class UrlReaderParams(BaseModel):
    url_type: Optional[UrlReaderType] = UrlReaderType.PUBLIC_URL_READER
    urls: List[str]

    model_config = ConfigDict(from_attributes=True)
