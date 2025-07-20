from pathlib import Path
from typing import Dict
import shutil
from deputydev_core.utils.app_logger import AppLogger
from deputydev_core.services.ide_review.dataclass.main import FileChangeStatusTypes
from .base import DiffSnapshotBase
from app.constants import FILE_SNAPSHOT_PATH
from app.constants import COMMIT_SNAPSHOT_PATH
from app.constants import DIFF_SNAPSOT_PATH


class LocalDiffSnapshot(DiffSnapshotBase):
    """Utility class for managing file snapshots during diff operations.
    
    This class handles creating, retrieving, and cleaning up snapshots of files
    during diff operations in a git repository.
    
    Args:
        repo_path (Path): Path to the git repository
        source_branch (str): Name of the source branch for snapshots
    """
    def __init__(self, repo_path: str, source_branch: str) -> None:
        self._repo_path = Path(repo_path).resolve()
        self._snapshot_path: Optional[Path] = None
        self._source_branch = source_branch
    
    @property
    def snapshot_path(self):
        """Builds the snapshot path for the given source branch."""
        if not self._snapshot_path:
            self._snapshot_path = self._repo_path / FILE_SNAPSHOT_PATH / self._source_branch
        return self._snapshot_path

    
    def take_diff_snapshot(self, file_change_map: Dict[str, FileChangeStatusTypes]):
        """Takes a snapshot of files based on their change status.
        
        Args:
            file_change_map (Dict[str, FileChangeStatusTypes]): Mapping of file paths to their change status
            
        Raises:
            Exception: If snapshot creation fails
        """
        try:
            # Remove previous snapshot if exists
            if self.snapshot_path.exists() and self.snapshot_path.is_dir():
                shutil.rmtree(self.snapshot_path)
            
            # Create snapshot directory
            self.snapshot_path.mkdir(parents=True, exist_ok=True)
            
            # Write the status snapshot file
            with open(self.snapshot_path  / DIFF_SNAPSOT_PATH, "w") as f:
                for file, status in file_change_map.items():
                    f.write(f"{status.value} {file}\n")

            # Copy files to snapshot directory
            for file in file_change_map:
                path = Path(file)
                # Copy which files exists
                if path.is_file():
                    full_dest = self.snapshot_path / file
                    full_dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(file, full_dest)
        except Exception as ex:
            AppLogger.log_error(f"Diff snapshot failed with error {ex}")
            raise Exception(f"Diff snapshot failed with error {ex}")
            

    def get_previous_snapshot(self) -> set[str]:
        """Retrieves the set of files from the previous snapshot.
        
        Returns:
            set[str]: Set of file paths from the previous snapshot
        """
        previous_snapshot = self.snapshot_path / DIFF_SNAPSOT_PATH
        prev_files: set[str] = set({})
        # If previous snapshot exists
        if previous_snapshot.exists():
            # Read the status snapshot file
            with open(previous_snapshot) as f:
                # Get the file paths from the snapshot
                prev_files = set([line.strip().split(" ")[1] for line in f])

        return prev_files 
    
    def get_snapshot_path(self) -> Path:
        """Gets the path where snapshots are stored.
        
        Returns:
            Path: Path to the snapshot directory
        """
        return self.snapshot_path
    
    def clean(self):
        """Removes all snapshots for the current branch."""
        if self.snapshot_path.exists():
            shutil.rmtree(self.snapshot_path)
            
    def take_commit_snapshot(self, commit_id: str) -> None:
        """Takes a snapshot of the current commit ID.
        
        Args:
            commit_id (str): The git commit ID to snapshot
        """
        self.snapshot_path.mkdir(parents=True, exist_ok=True)
        with open(self.snapshot_path  / COMMIT_SNAPSHOT_PATH, "w") as f:
            f.write(f"{commit_id}")
        
    
    def get_last_reviewed_commit_id(self) -> str | None:
        """Gets the last reviewed commit ID.
        
        Returns:
            str: The last reviewed commit ID, or empty string if no commit was reviewed
        """
        self.snapshot_path.mkdir(parents=True, exist_ok=True)
        commit_file = self.snapshot_path / COMMIT_SNAPSHOT_PATH
        
        if not commit_file.exists():
            return 

        with open(commit_file, "r") as f:
            return f.read().strip()
        