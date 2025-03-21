from typing import List, Optional

from pydantic import BaseModel
from deputydev_core.services.chunking.chunk_info import ChunkInfo


class RelevantChunksParams(BaseModel):
    repo_path: str
    auth_token: str
    query: str
    focus_chunks: Optional[List[str]] = []
    focus_files: Optional[List[str]] = []
    focus_directories: Optional[List[str]] = []
    perform_chunking: Optional[bool] = False


class ChunkInfoAndHash(BaseModel):
    chunk_info: ChunkInfo
    chunk_hash: str
