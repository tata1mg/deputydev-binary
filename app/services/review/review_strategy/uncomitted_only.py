from app.services.review.diff_utils import get_commit_changes
from app.services.review.review_strategy.base import BaseStrategy
from app.services.review.dataclass.main import FileChanges  
from typing import List
from app.services.review.dataclass.main import FileChangeStatusTypes
from typing import Dict
from app.services.review.diff_utils import get_file_diff, clean_diff, format_diff_response
from app.services.review.dataclass.main import FILE_DIFF_STATUS_MAP
from deputydev_core.utils.app_logger import AppLogger


class UncomittedOnlyStrategy(BaseStrategy):
    def get_diff_changes(self) -> List[FileChanges]:
        return get_changes( self._snapshot_utils, self._git_utils)
    
    def snapshot(self):
        self._snapshot_utils.take_diff_snapshot()

    def reset(self):
        self._snapshot_utils.clean()    
    
    def get_comparable_commit(self) -> str:
        return self.source_commit
    
    def get_diff_changes(self) -> List[FileChanges]:

        """
        Returns:
            List[FileChanges]: List of file changes
        """

        git_repo = self._git_utils.git_repo
        prev_files = self._snapshot_utils.get_previous_snapshot()
        current_changes = self.get_uncommited_changes()
        
        current_changed_files = set(current_changes.keys())
        changes: List[FileChanges] = []

        # Check modified files
        for file in prev_files & current_changed_files:
            file_path = Path(file)
            snap_file = self._snapshot_utils.get_snapshot_path() / file
            if file_path.is_file() and snap_file.is_file() and not compare_files(file_path, snap_file):
                try:
                    diff = get_file_diff(git_repo, file, current_changes[file], self.get_comparable_commit())
                    changes.append(format_diff_response(file, diff, current_changes[file]))
                except Exception as e:
                    AppLogger.error(f"Error getting diff for {file}: {e}")

        # Check newly changed files (not in snapshot before)
        for file in current_changed_files - prev_files:
            try:
                diff = get_file_diff(git_repo, file, current_changes[file], self.get_comparable_commit())
                # diff = clean_diff(diff)
                changes.append(format_diff_response(file, diff, current_changes[file]))
            except Exception as e:
                AppLogger.error(f"Error getting diff for {file}: {e}")
        
        return changes
    
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
