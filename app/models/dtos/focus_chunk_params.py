from typing import List, Optional, Union

from deputydev_core.services.chunking.chunk_info import ChunkInfo
from pydantic import BaseModel
from deputydev_core.services.chunking.dataclass.main import ChunkMetadata


class ChunkDetails(BaseModel):
    start_line: int
    end_line: int
    chunk_hash: str
    file_path: str
    file_hash: str
    meta_info: Optional[ChunkMetadata] = None


class CodeSnippetDetails(BaseModel):
    unique_snippet_identifier: str
    start_line: int
    end_line: int
    file_path: str


class FocusChunksParams(BaseModel):
    repo_path: str
    chunks: List[Union[ChunkDetails, CodeSnippetDetails]]


class ChunkInfoAndHash(BaseModel):
    chunk_info: ChunkInfo
    chunk_hash: str
