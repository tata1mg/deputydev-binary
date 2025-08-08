import json
from typing import Any, Dict

from deputydev_core.services.file_summarization.file_summarization_service import (
    FileSummarizationService,
)
from deputydev_core.services.tools.iterative_file_reader.dataclass.main import (
    FileSummaryReaderRequestParams,
    IterativeFileReaderRequestParams,
    IterativeFileReaderResponse,
)
from deputydev_core.services.tools.iterative_file_reader.iterative_file_reader import (
    IterativeFileReader,
)
from sanic import Blueprint, HTTPResponse
from sanic.exceptions import BadRequest
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
    validated_body = IterativeFileReaderRequestParams(**json_body)
    file_reader: IterativeFileReaderResponse = await IterativeFileReader(
        file_path=validated_body.file_path,
        repo_path=validated_body.repo_path,
    ).read_lines(start_line=validated_body.start_line, end_line=validated_body.end_line)

    response: Dict[str, Any] = {
        "data": {
            "chunk": file_reader.chunk.model_dump(mode="json"),
            "eof_reached": file_reader.eof,
            "was_summary": file_reader.was_summary,
            "total_lines": file_reader.total_lines,
        },
    }
    return HTTPResponse(body=json.dumps(response))


@codebase_read.route("/read-file-or-summary", methods=["POST"])
@get_error_handler(special_handlers=[])
async def read_file_or_summary(_request: Request) -> HTTPResponse:
    json_body = _request.json
    if not json_body:
        raise BadRequest("Request payload is missing or invalid.")
    validated_body = FileSummaryReaderRequestParams(**json_body)

    file_path = validated_body.file_path
    repo_path = validated_body.repo_path or ""
    number_of_lines = validated_body.number_of_lines or 100
    start_line = validated_body.start_line
    end_line = validated_body.end_line

    reader = IterativeFileReader(file_path=file_path, repo_path=repo_path)
    total_lines = await reader.count_total_lines()

    # If a specific region is requested, return that region
    if start_line is not None and end_line is not None:
        file_reader_response: IterativeFileReaderResponse = await reader.read_lines(start_line, end_line)
        response: Dict[str, Any] = {
            "type": "selection",
            "content": file_reader_response.chunk.content,
            "total_lines": total_lines,
            "start_line": start_line,
            "end_line": end_line,
        }
        return HTTPResponse(body=json.dumps(response))

    # If the whole file is requested and it's under the threshold, return the full content
    if (start_line is None and end_line is None) and total_lines <= number_of_lines:
        file_reader_response: IterativeFileReaderResponse = await reader.read_lines(1, total_lines)
        response: Dict[str, Any] = {
            "type": "full",
            "content": file_reader_response.chunk.content,
            "total_lines": total_lines,
        }
        return HTTPResponse(body=json.dumps(response))

    # Otherwise, return a summary
    summary = await FileSummarizationService.summarize_file(
        file_path, repo_path, max_lines=200, include_line_numbers=True
    )
    response: Dict[str, Any] = {
        "type": "summary",
        "content": summary.summary_content,
        "total_lines": total_lines,
    }
    return HTTPResponse(body=json.dumps(response))
