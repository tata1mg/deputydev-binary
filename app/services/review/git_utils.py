import subprocess
from git import Repo
from git import Repo, InvalidGitRepositoryError, NoSuchPathError
from typing import List



class GitUtils:
    def __init__(self, repo_path: str):
        self._repo_path = repo_path
        self.git_repo = Repo(self._repo_path)
        self._source_branch: str = None #type: ignore
        

    def get_default_branch(self) -> str:
        """
        Returns the default branch (e.g., 'main' or 'master') as set by origin/HEAD.
        """
        ref = subprocess.check_output(
            "git symbolic-ref refs/remotes/origin/HEAD",
            cwd=self._repo_path,
            shell=True,
            text=True
        ).strip()
        return ref.split("/")[-1]

    
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

        all_branches:List[str] = []

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
        matches = [b for b in all_branches if keyword in b]

        # Return sorted unique branch names
        return sorted(set(matches))
    