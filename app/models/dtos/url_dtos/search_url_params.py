from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.utils.constant.url_constants import UrlType


class SearchUrlParams(BaseModel):
    keyword: str
    limit: Optional[int] = 5
