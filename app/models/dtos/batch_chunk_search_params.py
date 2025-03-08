from typing import List, Optional
from pydantic import BaseModel


class SearchTerm(BaseModel):
    keyword: str
    type: str
    file_path: Optional[str] = None


class BatchSearchParams(BaseModel):
    repo_path: str
    search_terms: List[SearchTerm]