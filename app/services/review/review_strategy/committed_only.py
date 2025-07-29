from typing import Dict, List, Optional

from app.services.review.dataclass.main import FILE_DIFF_STATUS_MAP, FileChanges, FileChangeStatusTypes
from app.services.review.diff_utils import format_diff_response

from .base import BaseStrategy


class CommittedOnlyStrategy(BaseStrategy):
    def reset(self):
        """
        Reset the current review state
        """
        self._snapshot_utils.clean()

    def snapshot(self, target_branch: Optional[str] = None) -> None:
        """
        Take diff snapshot
        Take commit snapshot
        """
        self._snapshot_utils.take_commit_snapshot(self.source_commit, target_branch)

    def get_diff_changes(self) -> List[FileChanges]:
        """
        target_branch: str :  Target branch to get the changes from
        last_review_commit_id: Optional[str] = None : Last reviewed commit id
        Returns:
            List[FileChanges]: List of file changes
        """
        repo = self._git_utils.git_repo

        # Get the file change status between source and target commit
        print("target_commit", self.target_commit)
        print("source_commit", self.source_commit)
        name_status_output = repo.git.diff("--name-status", self.target_commit, self.source_commit)

        results: List[FileChanges] = []

        # Parse the name-status output
        for line in name_status_output.strip().split("\n"):
            # Skip empty lines
            if not line:
                continue

            # Split the line into parts
            parts = line.split("\t")
            # The actual line looks like this
            # M	file1.py
            # A	file2.py
            # D	file3.py

            if len(parts) < 2:
                continue

            # Get the change type and file path
            change_type, file_path = parts[0], parts[1]
            # Get diff for this specific using commit
            file_diff = repo.git.diff(self.target_commit, self.source_commit, "--", file_path)
            results.append(format_diff_response(file_path, file_diff, FILE_DIFF_STATUS_MAP.get(change_type, "A")))
        return results

    def get_uncommited_changes(self) -> Dict[str, FileChangeStatusTypes]:
        return {}
