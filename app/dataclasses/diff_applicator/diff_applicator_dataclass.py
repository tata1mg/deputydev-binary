from typing import List

from deputydev_core.services.diff.dataclasses.main import FileDiffApplicationRequest
from pydantic import BaseModel


class DiffApplicatorInput(BaseModel):
    diff_application_requests: List[FileDiffApplicationRequest]
