from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CacheHeaders(BaseModel):
    etag: Optional[str] = None
    last_modified: Optional[str] = None


class UrlsContentDto(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    url: str
    content: Optional[str] = None
    last_indexed: Optional[datetime] = None
    cache_headers: Optional[CacheHeaders] = None
    content_hash: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
