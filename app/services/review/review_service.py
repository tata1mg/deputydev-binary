from deputydev_core.services.ide_review.diff_selector.diff_manager import DiffChangeTracker

from app.utils.request_handlers import handle_ide_review_exceptions


class ReviewService:
    @classmethod
    @handle_ide_review_exceptions
    async def get_diff_summary(cls, repo_path, target_branch, review_type):
        diff_manager = DiffChangeTracker(repo_path)
        response = {
            "changes": diff_manager.get_review_changes(target_branch=target_branch, review_type=review_type),
            "source_branch": diff_manager.get_source_branch(),
            "target_branch": target_branch  or diff_manager.get_default_branch()
        }
        return response

    @classmethod
    @handle_ide_review_exceptions
    async def get_source_branch(cls, repo_path):
        return DiffChangeTracker(repo_path).get_source_branch()

    @classmethod
    @handle_ide_review_exceptions
    async def search_branches(cls, repo_path, keyword):
        return DiffChangeTracker(repo_path).search_branch(keyword=keyword)

