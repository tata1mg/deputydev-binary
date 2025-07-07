from typing import Optional

from pydantic import BaseModel


class SearchUrlParams(BaseModel):
    keyword: str
    limit: Optional[int] = 5
