from typing import Optional

from pydantic import BaseModel


class ListUrlParams(BaseModel):
    limit: Optional[int] = 5
    offset: Optional[int] = 0
