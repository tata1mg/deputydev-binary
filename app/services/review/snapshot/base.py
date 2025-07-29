from abc import ABC
from pathlib import Path
from app.services.review.dataclass.main import FileChangeStatusTypes
from typing import Dict
from abc import abstractmethod



class DiffSnapshotBase(ABC):
    def __init__(self, repo_path: str, source_branch: str) -> None:
        self._repo_path = repo_path
        self.snapshot_path = self._repo_path / ".git" / "file-snapshots" / source_branch
    
    @abstractmethod
    def take_temp_diff_snapshot(self, status_map: Dict[str, FileChangeStatusTypes]):
        """Takes a snapshot of files based on their change status."""
        raise NotImplementedError

    @abstractmethod
    def take_diff_snapshot(self,) -> str:
        """Takes a snapshot of files based on their change status.
            
        Returns:
            str: Success message if snapshot is completed
            
        Raises:
            Exception: If snapshot creation fails
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_previous_snapshot(self) -> Dict[str, FileChangeStatusTypes]:
        """
        Returns:
            Dict[str, FileChangeStatusTypes]: Mapping of file paths to their change status
        """
        raise NotImplementedError
    
    @abstractmethod
    def clean(self):
        """
        Removes all snapshots for the current branch.
        """
        raise NotImplementedError
    
    @abstractmethod
    def take_commit_snapshot(self, commit_id: str, target_branch: str):
        """Takes a snapshot of the current commit ID.
        
        Args:
            commit_id (str): The git commit ID to snapshot
            target_branch (str): The target branch this commit belongs to
        
        Raises:
            Exception: If snapshot creation fails
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_last_reviewed_commit_id(self, target_branch: str) -> str:
        """
        Args:
            target_branch (str): The target branch to get commit for
        
        Returns:
            str: The last reviewed commit ID, or empty string if no commit was reviewed

        Raises:
            Exception: If snapshot creation fails
        """
        raise NotImplementedError   
