from typing import List, Optional
from pydantic import BaseModel


class GrepSearchRequestParams(BaseModel):
    """
    Request parameters for the GrepSearch.
    """
    directory_path: str
    repo_path: str
    search_terms: Optional[List[str]] = None

class GrepSearchResponse(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    match_line: int
    content: str
