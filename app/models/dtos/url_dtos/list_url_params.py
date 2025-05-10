from pydantic import BaseModel
from typing import Optional


class ListUrlParams(BaseModel):
    limit: Optional[int] = 5
    offset: Optional[int] = 0
