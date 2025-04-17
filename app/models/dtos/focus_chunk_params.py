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
    search_item_name: Optional[str] = None
    search_item_type: Optional[str] = None
    chunks: List[Union[ChunkDetails, CodeSnippetDetails]]


class ChunkInfoAndHash(BaseModel):
    chunk_info: ChunkInfo
    chunk_hash: str

    def __hash__(self):
        return int.from_bytes(self.chunk_hash.encode(), byteorder='big')
