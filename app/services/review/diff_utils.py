import difflib
from pathlib import Path
from typing import Dict, Tuple

from deputydev_core.utils.app_logger import AppLogger
from git import Optional, Repo

from app.services.review.dataclass.main import FILE_DIFF_STATUS_MAP, FileChanges, FileChangeStatusTypes, LineChange


def count_added_removed_lines_changed(diff_text: str) -> Tuple[int, int]:
    # not used now
    added: int = 0
    deleted: int = 0
    for line in diff_text.splitlines():
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            continue
        if line.startswith("+"):
            added += 1
        elif line.startswith("-"):
            deleted += 1
    return added, deleted


def format_diff_response(file_path: str, diff: str, change_type: FileChangeStatusTypes) -> FileChanges:
    added, removed = count_added_removed_lines_changed(diff)
    file_change = FileChanges(
        file_path=file_path,
        file_name=Path(file_path).name,
        diff=diff,
        status=change_type,
        line_changes=LineChange(added=added, removed=removed),
    )
    return file_change


def clean_diff(diff_output: str) -> str:
    """Remove the first 4 lines from diff output (equivalent to tail -n +5)"""
    # lines = diff_output.split('\n')
    # return '\n'.join(lines[4:]) if len(lines) > 4 else ''
    return diff_output


def compare_files(file1: Path, file2: Path) -> bool:
    with open(file1, "r") as f1, open(file2, "r") as f2:
        return f1.read() == f2.read()


def get_file_diff(
    repo: Repo, file_path: str, change_type: FileChangeStatusTypes, commit_id: Optional[str] = None
) -> str:
    """Get diff for a specific file based on change type and commit reference."""
    commit_ref = commit_id or "HEAD"
    file_path_obj = Path(repo.working_tree_dir) / file_path  # type: ignore
    try:
        if change_type == FileChangeStatusTypes.UNTRACKED:
            # For untracked files, show diff against /dev/null
            if file_path_obj.is_file():
                return repo.git.diff("--no-index", "/dev/null", file_path, with_exceptions=False)
            else:
                return ""

        elif change_type == FileChangeStatusTypes.REMOVED:
            # For deleted files, show what was removed
            return repo.git.diff(commit_ref, "--", file_path)

        elif change_type == FileChangeStatusTypes.MODIFIED:
            # For modified files, check if we're dealing with staged vs unstaged changes
            if commit_id:
                # Compare specific commit to workspace
                return repo.git.diff(commit_ref, file_path)
            else:
                # Default behavior: show unstaged changes or staged changes
                if file_path_obj.is_file():
                    # Try unstaged changes first
                    unstaged_diff = repo.git.diff(file_path)
                    if unstaged_diff:
                        return unstaged_diff
                    # If no unstaged changes, show staged changes
                    return repo.git.diff("--cached", file_path)
                else:
                    return repo.git.diff("HEAD", "--", file_path)

        elif change_type == FileChangeStatusTypes.ADDED:
            if commit_id:
                # Compare from specific commit (file didn't exist then)
                return repo.git.diff("--no-index", "/dev/null", file_path, with_exceptions=False)
            else:
                # Show staged addition or diff from HEAD
                if file_path_obj.is_file():
                    cached_diff = repo.git.diff("--cached", file_path)
                    if cached_diff:
                        return cached_diff
                    return repo.git.diff("--no-index", "/dev/null", file_path, with_exceptions=False)
                else:
                    return repo.git.diff("HEAD", "--", file_path)

        elif change_type == FileChangeStatusTypes.RENAMED:
            # For renamed files, show the rename diff
            return repo.git.diff(commit_ref, "--", file_path)

        else:
            # Fallback for other change types
            return repo.git.diff(commit_ref, file_path)

    except Exception as e:
        AppLogger.log_error(f"Error generating diff for {file_path}: {e}")
        return ""


def get_current_changes_new(repo: Repo, commit_id: Optional[str] = None) -> Dict[str, FileChangeStatusTypes]:
    """Get current changes, optionally compared to a specific commit."""
    commit_ref = commit_id or "HEAD"
    file_change_status_map: Dict[str, FileChangeStatusTypes] = {}
    if commit_id:
        try:
            # Get changes from commit directly to working directory
            for diff in repo.commit(commit_ref).diff(None):  # type: ignore
                path = diff.b_path if diff.b_path else diff.a_path  # type: ignore
                change_type = diff.change_type  # type: ignore
                enum_value = FILE_DIFF_STATUS_MAP.get(change_type)  # type: ignore
                if enum_value and path not in file_change_status_map:  # type: ignore
                    file_change_status_map[path] = enum_value

        except Exception as e:
            print(f"Error getting changes from commit {commit_ref}: {e}")
    else:
        # Staged changes
        for diff in repo.index.diff(commit_ref):  # type: ignore
            path = diff.b_path if diff.b_path else diff.a_path  # type: ignore
            change_type = diff.change_type  # type: ignore
            enum_value = FILE_DIFF_STATUS_MAP.get(change_type)  # type: ignore
            if enum_value:
                file_change_status_map[path] = enum_value

        # Unstaged changes
        for diff in repo.index.diff(None):  # type: ignore
            path = diff.b_path if diff.b_path else diff.a_path  # type: ignore
            change_type = diff.change_type  # type: ignore
            enum_value = FILE_DIFF_STATUS_MAP.get(change_type)  # type: ignore
            # Only add if not already staged, or mark as modified if different from staged
            if enum_value:
                if path in file_change_status_map:
                    file_change_status_map[path] = FileChangeStatusTypes.MODIFIED
                else:
                    file_change_status_map[path] = enum_value

    for file in repo.untracked_files:
        file_change_status_map[file] = FileChangeStatusTypes.UNTRACKED

    return file_change_status_map


def get_file_diff_between_files(file_path: Path, snap_file: Path, abs_file_path: str) -> str:
    with file_path.open("r") as f1, snap_file.open("r") as f2:
        f1_lines = f1.readlines()
        f2_lines = f2.readlines()

    fromfile = f"a/{abs_file_path}"
    tofile = f"b/{abs_file_path}"

    diff = difflib.unified_diff(
        f2_lines,  # old file (snapshot)
        f1_lines,  # new file (current)
        fromfile=fromfile,
        tofile=tofile,
        lineterm="",
    )

    return "\n".join(diff)
