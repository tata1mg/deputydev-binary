from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.utils.constant.url_constants import UrlType


class UrlReaderParams(BaseModel):
    url_type: Optional[UrlType] = UrlType.PUBLIC_URL
    urls: List[str]

    model_config = ConfigDict(from_attributes=True)
