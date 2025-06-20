from typing import List

from deputydev_core.services.diff.dataclasses.main import (
    FileDiffApplicationRequest,
    FileDiffApplicationResponse,
)
from deputydev_core.services.diff.diff_applicator import DiffApplicator
from deputydev_core.utils.app_logger import AppLogger


class DiffApplicatorService:
    async def apply_diff(
        self,
        diff_application_requests: List[FileDiffApplicationRequest],
    ) -> List[FileDiffApplicationResponse]:
        try:
            # Apply diffs to multiple files in bulk
            responses = await DiffApplicator.bulk_apply_diff(diff_application_requests)
            return responses
        except Exception as _ex:
            AppLogger.log_error(f"Error while applying diff: {_ex}")
            raise _ex
