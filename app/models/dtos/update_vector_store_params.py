from typing import List, Optional

from pydantic import BaseModel


class UpdateVectorStoreParams(BaseModel):
    repo_path: str
    chunkable_files: Optional[List[str]] = []
