from abc import ABC
from typing import Optional

from sanic.response import HTTPResponse


class BaseErrorTypeHandler(ABC):
    """
    Base class for error type handlers.
    This class should be inherited by all specific error type handlers.
    """

    @staticmethod
    def handle_error(error: Exception) -> Optional[HTTPResponse]:
        """
        Handle the given error.
        This method should be implemented by subclasses to provide specific error handling logic.

        :param error: The error to handle
        :raises NotImplementedError: If the method is not implemented in a subclass
        """
        raise NotImplementedError("Subclasses must implement this method.")
