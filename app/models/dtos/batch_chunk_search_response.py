from typing import List, Optional
from pydantic import BaseModel
from deputydev_core.services.chunking.chunk_info import ChunkInfo


class BatchSearchResponse(BaseModel):
    keyword: str
    type: str
    file_path: Optional[str] = None
    chunks: List[ChunkInfo]
