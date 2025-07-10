import json
from typing import Any, Dict

from deputydev_core.services.file_summarization.file_summarization_service import (
    FileSummarizationService,
)
from deputydev_core.services.tools.iterative_file_reader.dataclass.main import (
    FileSummaryReaderRequestParams,
    IterativeFileReaderRequestParams,
)
from deputydev_core.services.tools.iterative_file_reader.iterative_file_reader import (
    IterativeFileReader,
)
from sanic import Blueprint, HTTPResponse
from sanic.exceptions import BadRequest, ServerError
from sanic.request import Request

from app.utils.route_error_handler.error_type_handlers.tool_handler import ToolErrorHandler
from app.utils.route_error_handler.route_error_handler import get_error_handler

codebase_read = Blueprint("codebase_read", url_prefix="")


@codebase_read.route("/iteratively-read-file", methods=["POST"])
@get_error_handler(special_handlers=[ToolErrorHandler])
async def read_file(_request: Request) -> HTTPResponse:
    json_body = _request.json
    if not json_body:
        raise BadRequest("Request payload is missing or invalid.")
    try:
        validated_body = IterativeFileReaderRequestParams(**json_body)
    except Exception:  # noqa: BLE001
        raise BadRequest("INVALID_PARAMS")

    try:
        file_content, eof_reached = await IterativeFileReader(
            file_path=validated_body.file_path,
            repo_path=validated_body.repo_path,
        ).read_lines(start_line=validated_body.start_line, end_line=validated_body.end_line)

        response: Dict[str, Any] = {
            "data": {
                "chunk": file_content.model_dump(mode="json"),
                "eof_reached": eof_reached,
            },
        }
        return HTTPResponse(body=json.dumps(response))
    except ValueError as ve:
        raise ValueError(ve)
    except Exception as e:  # noqa: BLE001
        raise ServerError(str(e)) from e


@codebase_read.route("/read-file-summary", methods=["POST"])
async def read_file_summary(_request: Request) -> HTTPResponse:
    json_body = _request.json
    if not json_body:
        raise BadRequest("Request payload is missing or invalid.")
    try:
        validated_body = FileSummaryReaderRequestParams(**json_body)
    except Exception:  # noqa: BLE001
        raise BadRequest("INVALID_PARAMS")

    try:
        file_summary = await FileSummarizationService().summarize_file(
            file_path=validated_body.file_path, include_line_numbers=True
        )

        return HTTPResponse(body=json.dumps(file_summary.model_dump(mode="json")))
    except ValueError as ve:
        raise ValueError(ve)
    except Exception as e:  # noqa: BLE001
        raise ServerError(str(e)) from e
