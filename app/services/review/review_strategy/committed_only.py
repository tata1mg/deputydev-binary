from .base import BaseStrategy
from app.services.review.dataclass.main import FileChanges
from app.services.review.dataclass.main import FILE_DIFF_STATUS_MAP
from app.services.review.snapshot.base import DiffSnapshotBase
from typing import Optional, List
from app.services.review.diff_utils import format_diff_response

class CommittedOnlyStrategy(BaseStrategy):    
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
        self._snapshot_utils.take_commit_snapshot(self.target_commit)

    def get_diff_changes(self) -> List[FileChanges]:
        """
        target_branch: str :  Target branch to get the changes from
        last_review_commit_id: Optional[str] = None : Last reviewed commit id
        Returns:
            List[FileChanges]: List of file changes
        """
        repo = self._git_utils.git_repo

        # Get the file change status between source and target commit
        name_status_output = repo.git.diff('--name-status', self.target_commit, self.source_commit)
        
        results: List[FileChanges] = []
        
        # Parse the name-status output
        for line in name_status_output.strip().split('\n'):
            # Skip empty lines
            if not line:
                continue
                
            # Split the line into parts
            parts = line.split('\t')
            # The actual line looks like this
            # M	file1.py
            # A	file2.py
            # D	file3.py

            if len(parts) < 2:
                continue
            
            # Get the change type and file path
            change_type, file_path = parts[0], parts[1]
            # Get diff for this specific using commit
            file_diff = repo.git.diff(self.target_commit, self.source_commit, '--', file_path)
            results.append(format_diff_response(file_path, file_diff, FILE_DIFF_STATUS_MAP.get(change_type, 'A')))
        return results
    