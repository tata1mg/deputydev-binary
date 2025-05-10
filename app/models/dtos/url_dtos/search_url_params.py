from pydantic import BaseModel
from typing import Optional


class SearchUrlParams(BaseModel):
    keyword: str
    limit: Optional[int] = 5
