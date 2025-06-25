import json
import traceback
from typing import Dict, Optional

from deputydev_core.errors.tools.tool_errors import HandledToolError, UnhandledToolError
from sanic.response import HTTPResponse

from app.utils.route_error_handler.error_type_handlers.base_error_type_handler import BaseErrorTypeHandler


class ToolErrorHandler(BaseErrorTypeHandler):
    """
    Handles errors related to tool execution.
    """

    @staticmethod
    def handle_error(error: Exception) -> Optional[HTTPResponse]:
        """
        Handle the tool execution error and return a user-friendly message.

        Args:
            error (Exception): The exception raised during tool execution.

        Returns:
            HTTPResponse: A Sanic HTTP response with the error message.
        """
        if isinstance(error, HandledToolError):
            error_response: Dict[str, Optional[str]] = {
                "error_code": error.error_code,
                "error_subtype": error.error_subtype,
                "error_type": error.error_type,
                "error_message": str(error),
                "traceback": str(traceback.format_exc()),
            }
            return HTTPResponse(body=json.dumps(error_response), status=400)
        elif isinstance(error, UnhandledToolError):
            error_response: Dict[str, Optional[str]] = {
                "error_code": error.error_code,
                "error_type": error.error_type,
                "error_subtype": error.error_subtype,
                "error_message": str(error),
                "traceback": str(traceback.format_exc()),
            }
            return HTTPResponse(body=json.dumps(error_response), status=500)
