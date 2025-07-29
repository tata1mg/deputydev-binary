from app.services.review.review_strategy.base import BaseStrategy
from app.services.review.dataclass.main import FileChangeStatusTypes
from typing import Dict
from app.services.review.dataclass.main import FILE_DIFF_STATUS_MAP



class UncomittedOnlyStrategy(BaseStrategy):
    def reset(self) -> None:
        self._snapshot_utils.clean()    
    
    def get_comparable_commit(self) -> str:
        return self.source_commit
    
    def get_uncommited_changes(self) -> Dict[str, FileChangeStatusTypes]:
        """Get current changes, optionally compared to a specific commit."""
        file_change_status_map: Dict[str, FileChangeStatusTypes] = {}
        repo = self._git_utils.git_repo
        # Staged changes
        for diff in repo.index.diff(self.source_commit): # type: ignore
            path = diff.b_path if diff.b_path else diff.a_path # type: ignore
            change_type = diff.change_type # type: ignore
            enum_value = FILE_DIFF_STATUS_MAP.get(change_type) # type: ignore
            if enum_value:
                file_change_status_map[path] = enum_value

        # Unstaged changes
        for diff in repo.index.diff(None): # type: ignore
            path = diff.b_path if diff.b_path else diff.a_path # type: ignore
            change_type = diff.change_type # type: ignore
            enum_value = FILE_DIFF_STATUS_MAP.get(change_type) # type: ignore
            # Only add if not already staged, or mark as modified if different from staged
            if enum_value:
                if path in file_change_status_map:
                    file_change_status_map[path] = FileChangeStatusTypes.MODIFIED
                else:
                    file_change_status_map[path] = enum_value
                    
        for file in repo.untracked_files:
            file_change_status_map[file] = FileChangeStatusTypes.UNTRACKED

        return file_change_status_map
