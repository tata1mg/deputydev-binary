from deputydev_core.services.ide_review.diff_selector.diff_change_tracker import DiffChangeTracker


from app.utils.request_handlers import handle_ide_review_exceptions


class ReviewService:
    @classmethod
    @handle_ide_review_exceptions
    async def get_diff_summary(cls, repo_path, target_branch, review_type):
        diff_manager = DiffChangeTracker(repo_path)
        response = diff_manager.get_review_changes(target_branch=target_branch, review_type=review_type)
        return response

    @classmethod
    @handle_ide_review_exceptions
    async def search_branches(cls, repo_path, keyword):
        return DiffChangeTracker(repo_path).search_branch(keyword=keyword)
    
    @classmethod
    @handle_ide_review_exceptions
    async def reset(cls, repo_path):
        return DiffChangeTracker(repo_path).reset()
    
    @classmethod
    @handle_ide_review_exceptions
    async def start_review(cls, repo_path, review_type):
        return DiffChangeTracker(repo_path).take_diff_snapshot(review_type)