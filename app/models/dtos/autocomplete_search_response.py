from typing import List, Optional

from pydantic import BaseModel
from deputydev_core.services.chunking.dataclass.main import ChunkMetadata


class ChunkDetails(BaseModel):
    start_line: int
    end_line: int
    chunk_hash: str
    file_path: str
    file_hash: str
    meta_info: Optional[ChunkMetadata] = None


class CodeSymbol(BaseModel):
    type: str
    value: Optional[str] = None
    file_path: str
    chunks: List[ChunkDetails]
    score: float
    commit_hash: str
