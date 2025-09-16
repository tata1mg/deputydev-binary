from abc import ABC
from pathlib import Path
from typing import Dict, List, Optional

from deputydev_core.utils.app_logger import AppLogger
from deputydev_core.utils.config_manager import ConfigManager

from app.services.review.dataclass.main import FileChanges, FileChangeStatusTypes, FileDiffs
from app.services.review.diff_utils import (
    compare_files,
    format_diff_response,
    get_file_diff,
    get_file_diff_between_files,
)
from app.services.review.exceptions.review_exceptions import (
    ConflictError,
    InvalidGitRepositoryError,
    LargeDiffError,
)
from app.services.review.file_ignore_utils import should_ignore_file
from app.services.review.git_utils import GitUtils
from app.services.review.snapshot.base import DiffSnapshotBase


class BaseStrategy(ABC):
    def __init__(self, repo_path: str, diff_snapshot: DiffSnapshotBase, target_branch: Optional[str] = None) -> None:
        """
        Args:
            repo_path (str): Path to the git repository
        """
        self.repo_path = Path(repo_path).resolve()
        self._git_utils = GitUtils(repo_path)
        self._source_branch: Optional[str] = None
        self._target_branch: Optional[str] = target_branch  # type: ignore
        self._snapshot_utils: DiffSnapshotBase = diff_snapshot
        self._target_commit: str = None  # type: ignore
        self._source_commit: str = None  # type: ignore

    def snapshot(self, target_branch: Optional[str] = None) -> None:
        self._snapshot_utils.take_diff_snapshot()
        self._snapshot_utils.increment_review_count()

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
            self._target_branch = self._git_utils.get_default_branch()
        return self._target_branch

    def is_large_pr_diff(self, diff_changes: List[FileChanges]) -> None:
        """
        Returns:
            bool: True if the PR diff is large
        """
        diff_size = 0
        for diff_change in diff_changes:
            diff_size += len(diff_change.diff)
        # TODO: Uncomment before final release
        max_diff_size = ConfigManager.configs["CODE_REVIEW"]["MAX_DIFF_SIZE"]
        AppLogger.log_info(f"Diff size: {diff_size}")
        if diff_size > max_diff_size:
            raise LargeDiffError(
                f"PR diff is large. Max diff size allowed : {max_diff_size}, Actual diff size : {diff_size}"
            )

    async def run_validations(self) -> None:
        """
        Run validations on the repo
        """
        # Check if the repo is a valid git repo
        if not self._git_utils.is_git_repo():
            raise InvalidGitRepositoryError("Repo is not a valid git repo")

        # Check if the repo has conflicts
        if self._git_utils.has_conflicts():
            raise ConflictError("Repo has conflicts")

    def get_effective_pr_diff(self, diff_changes: List[FileChanges]) -> List[FileChanges]:
        """
        Returns:
            List[FileChanges]: List of file changes
        """
        for diff_change in diff_changes:
            if should_ignore_file(diff_change.file_path):
                diff_changes.remove(diff_change)
        return diff_changes

    async def get_changes(self) -> FileDiffs:
        """
        Returns:
            FileDiffs: File diffs
        """
        fail_message: Optional[str] = None
        diff_changes: List[FileChanges] = []
        try:
            await self.run_validations()

            diff_changes = self.get_diff_changes()

            # Remove ignored files
            diff_changes = self.get_effective_pr_diff(diff_changes)

            # Check if the PR diff is large
            self.is_large_pr_diff(diff_changes)
        except (LargeDiffError, ConflictError, InvalidGitRepositoryError) as ex:
            AppLogger.log_info(f"Error getting review changes: {ex}")
            fail_message = str(ex)
        except Exception as ex:  # noqa: BLE001
            AppLogger.log_error(f"Error getting review changes: {ex}")
            fail_message = str(ex)
        finally:
            return FileDiffs(
                eligible_for_review=fail_message is None,
                fail_message=fail_message,
                file_wise_changes=diff_changes,
                target_branch=self.target_branch,
                source_branch=self.source_branch,
                source_commit=self.source_commit,
                target_commit=self.target_commit,
                origin_url=self._git_utils.get_default_remote_name(),
                repo_name=self._git_utils.get_default_remote_name().split("/")[-1].split(".")[0]
                if self._git_utils.get_default_remote_name()
                else "Not Found",
                review_count=self._snapshot_utils.get_review_count(),
            )

    def get_comparable_commit(self) -> str:
        raise NotImplementedError

    def get_uncommited_changes(self) -> Dict[str, FileChangeStatusTypes]:
        """
        Returns:
            Dict[str, FileChangeStatusTypes]: Dict of file changes
        """
        raise NotImplementedError

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
            file_path = Path(self.repo_path / file)
            snap_file = self._snapshot_utils.snapshot_path / file
            if file_path.is_file() and snap_file.is_file() and not compare_files(file_path, snap_file):
                try:
                    diff = get_file_diff_between_files(file_path, snap_file, file)
                    changes.append(format_diff_response(file, diff, current_changes[file]))
                except Exception as e:  # noqa: BLE001
                    AppLogger.log_error(f"Error getting diff for {file}: {e}")

        # Check newly changed files (not in snapshot before)
        for file in current_changed_files - prev_files:
            try:
                diff = get_file_diff(git_repo, file, current_changes[file], self.get_comparable_commit())
                changes.append(format_diff_response(file, diff, current_changes[file]))
            except Exception as e:  # noqa: BLE001
                AppLogger.log_error(f"Error getting diff for {file}: {e}")

        self._snapshot_utils.take_temp_diff_snapshot(current_changes)
        return changes

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

        self._target_commit = self._snapshot_utils.get_last_reviewed_commit_id(self.target_branch)
        # If no last reviewed commit id is found, use the default branch commit

        if not self._target_commit:
            if self.target_branch:
                self._target_commit = self._git_utils.commit_hash(self.target_branch)
        return self._target_commit

    def reset(self) -> None:
        """
        Reset the current review state
        """
        self._snapshot_utils.clean()
