from typing import List, Optional

from pydantic import BaseModel


class CommentValidityParams(BaseModel):
    line_number: int
    repo_path: str
    file_path: str
    line_hash: str
