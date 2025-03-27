from enum import Enum
from typing import List, Optional

from deputydev_core.models.dto.chunk_file_dto import ChunkFileData
from pydantic import BaseModel


class SearchKeywordType(Enum):
    FUNCTION = "function"
    CLASS = "class"
    FILE = "file"
    DIRECTORY = "directory"


class FocusItem(BaseModel):
    type: SearchKeywordType
    value: Optional[str] = None
    path: str
    chunks: Optional[List[ChunkFileData]] = None
    score: float


class FocusSearchParams(BaseModel):
    type: Optional[SearchKeywordType] = None
    keyword: str
    repo_path: str
