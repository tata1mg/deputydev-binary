class LargeDiffException(Exception):
    """Exception raised when the diff is too large."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"{self.message}")


class  ConflictException(Exception):
    """Exception raised when there is a conflict."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"{self.message}")


class InvalidGitRepositoryError(Exception):
    """Exception raised when the review type is invalid."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"{self.message}")
