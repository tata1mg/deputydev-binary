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


class FocusChunksParams(BaseModel):
    repo_path: str
    chunks: List[ChunkDetails]
