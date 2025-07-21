from pydantic import BaseModel
from enum import  Enum
from typing import List, Optional


class ApplicableDiffRequest(BaseModel):
    source_commit: str
    destination_commit: str
    source_branch_name: str
    destination_branch_name: str
    repo_path: str


class Diff(BaseModel):
    raw_diff: str


class FileChangeStatusTypes(Enum):
    ADDED = "A"
    REMOVED = "D"
    MODIFIED = "M"
    RENAMED = "R"
    COPIED = "C"
    UNTRACKED = "A"
    UNMERGED = "U"


class ReviewTypes(Enum):
    ALL = "ALL"
    UNCOMMITTED_ONLY = "UNCOMMITTED_ONLY"
    COMMITTED_ONLY = "COMMITTED_ONLY"


class LineChange(BaseModel):
    added: Optional[int] = 0
    removed: Optional[int] = 0


class FileChanges(BaseModel):
    file_path: str
    file_name: str
    status: FileChangeStatusTypes
    line_changes: Optional[LineChange] = None
    diff: str


class FileDiffs(BaseModel):
    file_wise_changes: List[FileChanges]
    target_branch: str
    source_branch: str
    source_commit: str
    target_commit: str
    origin_url: str


FILE_DIFF_STATUS_MAP = {
    "A": FileChangeStatusTypes.ADDED,
    "D": FileChangeStatusTypes.REMOVED,
    "M": FileChangeStatusTypes.MODIFIED,
    "R": FileChangeStatusTypes.RENAMED,
    "C": FileChangeStatusTypes.COPIED,
    "U": FileChangeStatusTypes.UNMERGED,
    "??": FileChangeStatusTypes.UNTRACKED,
}


class ReviewRequest(BaseModel):
    repo_path: str
    target_branch: Optional[str] = None
    review_type: ReviewTypes
