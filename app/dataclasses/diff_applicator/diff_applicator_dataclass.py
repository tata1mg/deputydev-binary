from typing import List
from pydantic import BaseModel
from deputydev_core.services.diff.dataclasses.main import (
    FileDiffApplicationRequest,
)

class DiffApplicatorInput(BaseModel):
    diff_application_requests: List[FileDiffApplicationRequest]
