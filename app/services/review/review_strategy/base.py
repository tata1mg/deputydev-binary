from abc import ABC
from abc import abstractmethod
from app.services.review.dataclass.main import FileChanges
from app.services.review.git_utils import GitUtils
from pathlib import Path
from app.services.review.snapshot.base import DiffSnapshotBase
from app.services.review.dataclass.main import FileDiffs
from typing import Optional



class BaseStrategy(ABC):
    def __init__(self, repo_path: str, diff_snapshot: DiffSnapshotBase, target_branch: Optional[str] = None):
        """
        Args:
            repo_path (str): Path to the git repository
        """
        self.repo_path = Path(repo_path).resolve()
        self._git_utils = GitUtils(self.repo_path)
        self._source_branch: str = None #type: ignore
        self._target_branch: Optional[str] = target_branch #type: ignore
        self._snapshot_utils: DiffSnapshotBase = diff_snapshot
        self._target_commit: str = None #type: ignore
        self._source_commit: str = None #type: ignore
        
        
    @property
    def source_branch(self) -> str:
        """
        Property to get the source branch of the repository.

        Returns:
            str: The name of the source branch.
        """
        
        if self._source_branch is None:
            self._source_branch = self._git_utils.get_source_branch()
        return self._source_branch
    
    @property
    def target_branch(self) -> str:
        """
        Property to get the target branch of the repository.

        Returns:
            str: The name of the target branch.
        """
        if self._target_branch is None:
            self._target_branch = self._git_utils.get_origin_branch(self.source_branch)
        return self._target_branch
    
    async def get_changes(self) -> FileDiffs:
        """
        Returns:
            FileDiffs: File diffs
        """
        
        # Check if the repo is a valid git repo
        if not self._git_utils.is_git_repo():
            raise Exception("Repo is not a valid git repo")
        
        diff_changes =  self.get_diff_changes()
        
        # format the diff changes
        return FileDiffs(
            file_wise_changes=diff_changes,
            target_branch=self.target_branch, 
            source_branch=self.source_branch,
            source_commit=self.source_commit,
            target_commit=self.target_commit,
            origin_url=self._git_utils.get_default_remote_name(),
            repo_name=self._git_utils.get_default_remote_name().split("/")[-1].split(".")[0]
        )


    @abstractmethod
    def get_diff_changes(self) -> list[FileChanges]:
        """
        Returns:
            list[FileChanges]: List of file changes
        """
        raise NotImplementedError

    @property
    def source_commit(self) -> str:
        """
        Property to get the source commit of the repository.

        Returns:
            str: The commit hash of the source branch.
        """
        return self._git_utils.commit_hash(self.source_branch)
    
    @property
    def target_commit(self) -> str:
        """
        Property to get the target commit of the repository.

        Returns:
            str: The commit hash of the target branch.
        """
        if self._target_commit:
            return self._target_commit

        self._target_commit = self._snapshot_utils.get_last_reviewed_commit_id()

        # If no last reviewed commit id is found, use the default branch commit
        
        if not self._target_commit:
            if self.target_branch:
                self._target_commit = self._git_utils.commit_hash(self.target_branch)
            else:
                self._target_commit = self._git_utils.commit_hash(self._git_utils.get_default_branch())
        
        return self._target_commit
    
    
    @abstractmethod
    def reset(self):
        raise NotImplementedError

    @abstractmethod
    def snapshot(self):
        raise NotImplementedError
        