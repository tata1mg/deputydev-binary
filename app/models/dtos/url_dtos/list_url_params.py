from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.utils.constant.url_constants import UrlType


class ListUrlParams(BaseModel):
    limit: Optional[int] = 5
    offset: Optional[int] = 0
