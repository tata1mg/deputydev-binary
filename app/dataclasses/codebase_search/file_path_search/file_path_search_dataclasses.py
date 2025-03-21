from typing import Optional, List
from pydantic import BaseModel


class FilePathSearchPayload(BaseModel):
    repo_path: str
    directory: str
    search_terms: Optional[List[str]] = None
