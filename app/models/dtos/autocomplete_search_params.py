from typing import Optional

from pydantic import BaseModel


class AutocompleteSearchParams(BaseModel):
    type: Optional[str] = None
    keyword: str
    repo_path: str
