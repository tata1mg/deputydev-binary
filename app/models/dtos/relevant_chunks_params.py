from typing import List, Optional

from pydantic import BaseModel


class RelevantChunksParams(BaseModel):
    repo_path: str
    auth_token: str
    query: str
    focus_chunks: Optional[List[str]] = []
    focus_files: Optional[List[str]] = []
    perform_chunking: Optional[bool] = False
