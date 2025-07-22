from app.services.review.dataclass.main import FileChanges
from app.services.review.diff_utils import get_commit_changes
from app.services.review.review_strategy.uncomitted_only import UncomittedOnlyStrategy
from typing import List, Dict
from app.services.review.dataclass.main import FileChangeStatusTypes
from app.services.review.dataclass.main import FILE_DIFF_STATUS_MAP


class AllChangesStrategy(UncomittedOnlyStrategy):
    def get_diff_changes(self) -> List[FileChanges]:
        """
        Returns:
            List[FileChanges]: List of file changes
        """
        changes =  get_commit_changes(self._snapshot_utils, self._git_utils, self.target_commit)
        return changes
    
    def reset(self):
        """
        Reset the current review state
        """
        self._snapshot_utils.clean()

    def snapshot(self):
        """
        Take diff snapshot
        Take commit snapshot
        """
        # take diff snapshot
        self._snapshot_utils.take_diff_snapshot()
        # take commit snapshot
        self._snapshot_utils.take_commit_snapshot(self.target_commit)
    
    def get_comparable_commit(self) -> str:
        return self.target_commit

    def get_uncommited_changes(self) -> Dict[str, FileChangeStatusTypes]:
        for diff in repo.commit(commit_ref).diff(None): # type: ignore
            path = diff.b_path if diff.b_path else diff.a_path # type: ignore
            change_type = diff.change_type # type: ignore
            enum_value = FILE_DIFF_STATUS_MAP.get(change_type) # type: ignore
            if enum_value and path not in FILE_DIFF_STATUS_MAP: # type: ignore
                FILE_DIFF_STATUS_MAP[path] = enum_value