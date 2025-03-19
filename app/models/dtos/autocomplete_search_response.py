from typing import Dict, List, Optional

from pydantic import BaseModel


class ChunkRange(BaseModel):
    start_line: int
    end_line: int


class CodeSymbol(BaseModel):
    type: str
    value: Optional[str] = None
    file_path: str
    chunks: List[ChunkRange]
    score: float
    commit_hash: str
