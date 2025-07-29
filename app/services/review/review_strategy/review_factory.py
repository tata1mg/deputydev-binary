from app.services.review.dataclass.main import ReviewTypes
from app.services.review.review_strategy.all_changes import AllChangesStrategy
from app.services.review.review_strategy.base import BaseStrategy
from app.services.review.review_strategy.committed_only import CommittedOnlyStrategy
from app.services.review.review_strategy.uncomitted_only import UncomittedOnlyStrategy


class ReviewFactory:
    """
    Factory class for creating review strategies.
    """

    # Mapping of review types to their corresponding strategies
    review_strategies = {
        ReviewTypes.COMMITTED_ONLY: CommittedOnlyStrategy,
        ReviewTypes.UNCOMMITTED_ONLY: UncomittedOnlyStrategy,
        ReviewTypes.ALL: AllChangesStrategy,
    }

    @classmethod
    def get_strategy(cls, review_type: ReviewTypes) -> BaseStrategy:
        """
        Returns the strategy for the given review type.
        """
        if review_type not in cls.review_strategies:
            raise ValueError(f"Invalid review type: {review_type}")
        return cls.review_strategies.get(review_type)
