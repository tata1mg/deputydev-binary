from pydantic import BaseModel
from typing import Optional, List


class UpdateVectorStoreParams(BaseModel):
    repo_path: str
    auth_token: str
    chunkable_files: Optional[List[str]] = []
