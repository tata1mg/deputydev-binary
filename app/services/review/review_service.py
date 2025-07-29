from typing import List, Optional

from app.services.review.dataclass.main import FileDiffs
from app.services.review.git_utils import GitUtils
from app.services.review.review_strategy.base import BaseStrategy
from app.services.review.review_strategy.review_factory import ReviewFactory
from app.services.review.snapshot.local_snapshot import LocalDiffSnapshot
from app.utils.request_handlers import handle_ide_review_exceptions


class ReviewService:
    @classmethod
    def _get_review_strategy(
        cls, repo_path: str, review_type: str, target_branch: Optional[str] = None
    ) -> BaseStrategy:
        """
        review_type: str : Review type
        target_branch: Optional[str] : Target branch
        repo_path: str : Path to the git repository
        Returns the review strategy for the given review type and target branch.
        """
        source_branch = GitUtils(repo_path).get_source_branch()
        diff_snapshot = LocalDiffSnapshot(repo_path, source_branch)
        return ReviewFactory.get_strategy(review_type)(
            repo_path=repo_path, target_branch=target_branch, diff_snapshot=diff_snapshot
        )

    @classmethod
    @handle_ide_review_exceptions
    async def get_diff_summary(cls, repo_path: str, target_branch: str, review_type: str) -> FileDiffs:
        """
        repo_path: str : Path to the git repository
        target_branch: str : Target branch
        review_type: str : Review type
        Returns the diff summary for the given review type and target branch.
        """
        strategy = cls._get_review_strategy(repo_path, review_type, target_branch)
        return await strategy.get_changes()

    @classmethod
    @handle_ide_review_exceptions
    async def search_branches(cls, repo_path: str, keyword: str) -> List[str]:
        """
        repo_path: str : Path to the git repository
        keyword: str : Keyword to search for
        Returns a list of branches that match the keyword.
        """
        return GitUtils(repo_path).search_branches(keyword)

    @classmethod
    @handle_ide_review_exceptions
    async def reset(cls, repo_path: str, review_type: str, target_branch: str) -> None:
        """
        repo_path: str : Path to the git repository
        review_type: str : Review type
        target_branch: str : Target branch
        Resets the review session.
        """
        strategy = cls._get_review_strategy(repo_path, review_type, target_branch)
        strategy.reset()

    @classmethod
    @handle_ide_review_exceptions
    async def take_snapshot(cls, repo_path: str, review_type: str, target_branch: str) -> str:
        """
        repo_path: str : Path to the git repository
        review_type: str : Review type
        target_branch: str : Target branch
        Starts a new review session.
        """
        strategy = cls._get_review_strategy(repo_path, review_type, target_branch)
        return strategy.snapshot(target_branch)
