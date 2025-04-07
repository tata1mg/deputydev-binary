from typing import Optional
from pydantic import BaseModel


class IterativeFileReaderRequestParams(BaseModel):
    """
    Request parameters for the IterativeFileReader.
    """

    file_path: str
    repo_path: str
    offset_line: Optional[int] = None
