from typing import Dict

from pydantic import BaseModel


class FocusChunksParams(BaseModel):
    repo_path: str
    auth_token: str
    file_path_to_commit_hashes: Dict[str, str]
