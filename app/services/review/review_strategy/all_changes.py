from typing import Dict, Optional

from app.services.review.dataclass.main import FILE_DIFF_STATUS_MAP, FileChangeStatusTypes
from app.services.review.review_strategy.uncomitted_only import UncomittedOnlyStrategy


class AllChangesStrategy(UncomittedOnlyStrategy):
    def snapshot(self, target_branch: Optional[str] = None) -> None:
        """
        Take diff snapshot
        Take commit snapshot
        """
        # take diff snapshot
        self._snapshot_utils.take_diff_snapshot()
        # take commit snapshot
        self._snapshot_utils.take_commit_snapshot(self.source_commit, target_branch)

    def get_comparable_commit(self) -> str:
        return self.target_commit

    def get_uncommited_changes(self) -> Dict[str, FileChangeStatusTypes]:
        file_change_status_map: Dict[str, FileChangeStatusTypes] = {}
        repo = self._git_utils.git_repo
        for diff in repo.commit(self.target_commit).diff(None):  # type: ignore
            path = diff.b_path if diff.b_path else diff.a_path  # type: ignore
            change_type = diff.change_type  # type: ignore
            enum_value = FILE_DIFF_STATUS_MAP.get(change_type)  # type: ignore
            if enum_value and path not in FILE_DIFF_STATUS_MAP:  # type: ignore
                file_change_status_map[path] = enum_value
        return file_change_status_map
