from typing import List, Optional
from pydantic import BaseModel


class Chunk(BaseModel):
    text: str
    start_line: int
    end_line: int


class BatchSearchResponse(BaseModel):
    keyword: str
    type: str
    file_path: Optional[str] = None
    chunks: List[Chunk]
