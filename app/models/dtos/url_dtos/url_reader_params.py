from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.utils.constant.url_constants import UrlType


class UrlReaderParams(BaseModel):
    url_type: Optional[UrlType] = UrlType.PUBLIC_URL
    urls: List[str]
    session_id: Optional[int] = None
    session_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
