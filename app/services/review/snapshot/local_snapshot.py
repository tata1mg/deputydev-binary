import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from deputydev_core.utils.app_logger import AppLogger

from app.constants import COMMIT_SNAPSHOT_PATH, DIFF_SNAPSOT_PATH, FILE_SNAPSHOT_PATH, SNAPSHOT_META
from app.services.review.dataclass.main import FileChangeStatusTypes

from .base import DiffSnapshotBase


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
    def snapshot_path(self) -> Path:
        """Builds the snapshot path for the given source branch."""
        if not self._snapshot_path:
            self._snapshot_path = self._repo_path / FILE_SNAPSHOT_PATH / self._source_branch
        return self._snapshot_path

    @property
    def temp_snapshot_path(self) -> Path:
        return self.snapshot_path / "temp"

    def take_temp_diff_snapshot(self, file_change_map: Dict[str, FileChangeStatusTypes]) -> None:
        """Takes a snapshot of files based on their change status.

        Args:
            file_change_map (Dict[str, FileChangeStatusTypes]): Mapping of file paths to their change status

        Raises:
            Exception: If snapshot creation fails
        """
        try:
            # Remove previous snapshot if exists
            if self.temp_snapshot_path.exists() and self.temp_snapshot_path.is_dir():
                shutil.rmtree(self.temp_snapshot_path)

            # Create snapshot directory
            self.temp_snapshot_path.mkdir(parents=True, exist_ok=True)

            # Write the status snapshot file
            with open(self.temp_snapshot_path / DIFF_SNAPSOT_PATH, "w") as f:  # noqa: PTH123
                for file, status in file_change_map.items():
                    f.write(f"{status.value} {file}\n")

            # Copy files to snapshot directory
            for file in file_change_map:
                path = Path(self._repo_path / file)
                # Copy which files exists
                if path.is_file():
                    full_dest = self.temp_snapshot_path / file
                    full_dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(path, full_dest)
        except Exception as ex:  # noqa: BLE001
            AppLogger.log_error(f"Diff snapshot failed with error {ex}")
            raise Exception(f"Diff snapshot failed with error {ex}")

    def take_diff_snapshot(self) -> None:
        """Takes a snapshot of files based on their change status."""
        """Moves contents of temp snapshot to snapshot path."""
        if self.temp_snapshot_path.exists():
            self.snapshot_path.mkdir(parents=True, exist_ok=True)

            for item in self.temp_snapshot_path.iterdir():
                dest = self.snapshot_path / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()

                shutil.move(str(item), str(dest))

            shutil.rmtree(self.temp_snapshot_path)

            # Increment review count after successful snapshot
            self._increment_review_count()

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
            with open(previous_snapshot) as f:  # noqa: PTH123
                # Get the file paths from the snapshot
                prev_files = set([line.strip().split(" ", 1)[1] for line in f])

        return prev_files

    def clean(self) -> None:
        """Removes all snapshots for the current branch"""
        if self.snapshot_path.exists():
            shutil.rmtree(self.snapshot_path)

    def take_commit_snapshot(self, commit_id: str, target_branch: str) -> None:
        """Takes a snapshot of the current commit ID for a specific branch.

        Args:
            commit_id (str): The git commit ID to snapshot
            target_branch (str): The target branch this commit belongs to
        """
        self.snapshot_path.mkdir(parents=True, exist_ok=True)

        # Load existing snapshots
        snapshots = self._load_snapshots()

        # Update the snapshot for this branch
        snapshots[target_branch] = {"commit_id": commit_id, "timestamp": datetime.now().isoformat()}

        # Save updated snapshots
        with open(self.snapshot_path / COMMIT_SNAPSHOT_PATH, "w") as f:  # noqa: PTH123
            json.dump(snapshots, f, indent=2)

    def get_last_reviewed_commit_id(self, target_branch: str = None) -> str | None:
        """Gets the last reviewed commit ID for a branch.

        Args:
            target_branch (str): The target branch to get commit for

        Returns:
            str: The last reviewed commit ID, or None if no commit was reviewed
        """
        if not target_branch:
            return None

        snapshots = self._load_snapshots()
        branch_data = snapshots.get(target_branch)

        return branch_data.get("commit_id") if branch_data else None

    def _load_snapshots(self) -> dict:
        """Loads the branch snapshots from file.

        Returns:
            dict: Dictionary with branch names as keys
        """
        commit_file = self.snapshot_path / COMMIT_SNAPSHOT_PATH

        if not commit_file.exists():
            return {}

        try:
            with open(commit_file, "r") as f:  # noqa: PTH123
                data = json.load(f)

                # If it's already a dict, return it
                if isinstance(data, dict):
                    return data
                else:
                    return {}

        except json.JSONDecodeError:
            # Handle old plain text format - migrate to new format
            try:
                with open(commit_file, "r") as f:  # noqa: PTH123
                    commit_id = f.read().strip()
                    if commit_id:
                        # Assume it was for 'main' branch
                        return {"main": {"commit_id": commit_id, "timestamp": datetime.now().isoformat()}}  # noqa: BLE001
            except Exception:  # noqa: BLE001
                pass

            return {}

    def _load_meta_data(self) -> dict:
        """Loads the snapshot metadata from file.

        Returns:
            dict: Dictionary containing metadata like review_count
        """
        meta_file = self.snapshot_path / SNAPSHOT_META

        if not meta_file.exists():
            return {}

        try:
            with open(meta_file, "r") as f:  # noqa: PTH123
                return json.load(f)
        except (json.JSONDecodeError, Exception):  # noqa: BLE001
            return {}

    def _save_meta_data(self, meta_data: dict) -> None:
        """Saves the snapshot metadata to file.

        Args:
            meta_data (dict): Dictionary containing metadata to save
        """
        try:
            self.snapshot_path.mkdir(parents=True, exist_ok=True)
            meta_file = self.snapshot_path / SNAPSHOT_META

            with open(meta_file, "w") as f:  # noqa: PTH123
                json.dump(meta_data, f, indent=2)
        except Exception as ex:  # noqa: BLE001
            AppLogger.log_error(f"Failed to save metadata: {ex}")

    def _increment_review_count(self) -> None:
        """Increments the review count in metadata."""
        meta_data = self._load_meta_data()
        current_count = meta_data.get("review_count", 0)
        meta_data["review_count"] = current_count + 1
        meta_data["last_review_timestamp"] = datetime.now().isoformat()
        self._save_meta_data(meta_data)
        AppLogger.log_info(f"Review count incremented to {meta_data['review_count']}")

    def get_review_count(self) -> int:
        """Gets the current review count.

        Returns:
            int: The number of reviews completed
        """
        meta_data = self._load_meta_data()
        return meta_data.get("review_count", 0)
