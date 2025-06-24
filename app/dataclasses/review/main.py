from typing import Optional

from pydantic import BaseModel
from deputydev_core.services.ide_review.dataclass.main import ReviewTypes


class ReviewRequest(BaseModel):
    repo_path: str
    target_branch: Optional[str] = None
    review_type: ReviewTypes
