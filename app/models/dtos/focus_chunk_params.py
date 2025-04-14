from typing import List, Optional, Union

from deputydev_core.services.chunking.chunk_info import ChunkInfo
from deputydev_core.services.chunking.dataclass.main import ChunkMetadata
from pydantic import BaseModel


class ChunkDetails(BaseModel):
    start_line: int
    end_line: int
    chunk_hash: str
    file_path: str
    file_hash: str
    meta_info: Optional[ChunkMetadata] = None


class CodeSnippetDetails(BaseModel):
    chunk_hash: str
    start_line: int
    end_line: int
    file_path: str


class FocusChunksParams(BaseModel):
    repo_path: str
    search_item_name: str
    search_item_type: str
    chunks: List[Union[ChunkDetails, CodeSnippetDetails]]


class ChunkInfoAndHash(BaseModel):
    chunk_info: ChunkInfo
    chunk_hash: str
