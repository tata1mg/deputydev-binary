from datetime import datetime
from typing import List

from git import InvalidGitRepositoryError, NoSuchPathError, Repo


class GitUtils:
    def __init__(self, repo_path: str) -> None:
        self._repo_path = repo_path
        self.git_repo = Repo(self._repo_path)
        self._source_branch: str = None  # type: ignore

    def has_conflicts(self) -> bool:
        """
        Returns True if there are conflicts in the index, False otherwise.
        """
        # Check for unmerged entries in the index
        unmerged_blobs = self.git_repo.index.unmerged_blobs()

        return bool(unmerged_blobs)

    def get_default_branch(self) -> str:
        """
        Returns the default branch (e.g., 'main' or 'master') as set by origin/HEAD.
        """
        origin = self.git_repo.remotes.origin
        head_ref = origin.refs.HEAD
        target_branch = head_ref.ref.name.split("/")[-1]
        return target_branch

    def get_origin_branch(self, branch_name: str) -> str:
        """
        Detects the most likely branch from which the given branch originated.
        It compares merge bases with all other branches and returns the one with the latest common ancestor.
        """
        repo = self.git_repo
        branches = [head.name for head in repo.heads if head.name != branch_name]
        latest_origin = None
        latest_time = None

        for candidate in branches:
            try:
                merge_base = repo.git.merge_base(branch_name, candidate).strip()
                commit = repo.commit(merge_base)
                commit_time = datetime.fromtimestamp(commit.committed_date)

                if not latest_time or commit_time > latest_time:
                    latest_time = commit_time
                    latest_origin = candidate
            except Exception: # noqa: BLEO01
                continue  # skip if branches don't have a merge base

        if latest_origin:
            return latest_origin
        else:
            # fallback — assume from default branch
            return self.get_default_branch()

    def get_default_remote_name(self) -> str:
        """
        Returns the fetch URL of the 'origin' remote.
        """
        origin = self.git_repo.remotes.origin
        return origin.url

    def commit_hash(self, branch_name: str) -> str:
        """
        Returns the latest commit hash for the given branch name, local or remote.
        """

        # Try local branch first
        if branch_name in self.git_repo.heads:
            commit = self.git_repo.heads[branch_name].commit
        # Then try remote branch
        elif f"origin/{branch_name}" in self.git_repo.refs:
            commit = self.git_repo.refs[f"origin/{branch_name}"].commit
        else:
            raise ValueError(f"Branch '{branch_name}' not found locally or on origin.")

        return commit.hexsha

    def is_git_repo(self) -> bool:
        try:
            _ = self.git_repo.git_dir
            return True
        except (InvalidGitRepositoryError, NoSuchPathError):
            return False

    def get_source_branch(self) -> str:
        if not self._source_branch:
            self._source_branch = self.git_repo.active_branch.name
        return self._source_branch

    def search_branches(self, keyword: str, add_remote: bool = False) -> List[str]:
        """
        Search for branches (local and remote) that contain the keyword.
        Returns a list of matching branch names (without 'origin/' prefix).
        """
        if not keyword:
            raise ValueError("Keyword cannot be empty")

        all_branches: List[str] = []

        # Local branches
        for head in self.git_repo.heads:
            all_branches.append(head.name)

        if add_remote:
            # Remote branches
            for remote in self.git_repo.remotes:
                for ref in remote.refs:
                    # Skip HEAD references (e.g., origin/HEAD)
                    if ref.name.endswith("/HEAD"):
                        continue
                    # Strip 'origin/' or other remote name prefix
                    branch_name = ref.name.split("/", 1)[1] if "/" in ref.name else ref.name
                    all_branches.append(branch_name)

        # Filter by keyword
        matches = []
        if all_branches:
            matches = [b for b in all_branches if keyword in b]

        # Return sorted unique branch names
        return sorted(set(matches))
