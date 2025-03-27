from typing import List, Optional

from deputydev_core.services.chunking.chunk_info import ChunkInfo
from pydantic import BaseModel


class BatchSearchResponse(BaseModel):
    keyword: str
    type: str
    file_path: Optional[str] = None
    chunks: List[ChunkInfo]
