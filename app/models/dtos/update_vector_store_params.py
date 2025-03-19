from typing import List, Optional

from pydantic import BaseModel


class UpdateVectorStoreParams(BaseModel):
    repo_path: str
    auth_token: str
    chunkable_files: Optional[List[str]] = []
    sync: Optional[bool] = False
