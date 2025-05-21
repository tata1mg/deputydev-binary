import json
import os

from app.utils.error_handler import error_handler
from sanic import Blueprint, HTTPResponse
from sanic.request import Request

from deputydev_core.services.tools.iterative_file_reader.dataclass.main import (
    IterativeFileReaderRequestParams,
)
from deputydev_core.services.tools.iterative_file_reader.iterative_file_reader import (
    IterativeFileReader,
)
from sanic.exceptions import BadRequest, ServerError
codebase_read = Blueprint("codebase_read", url_prefix="")


@codebase_read.route("/iteratively-read-file", methods=["POST"])
@error_handler
async def read_file(_request: Request):
    json_body = _request.json
    if not json_body:
        raise BadRequest("Request payload is missing or invalid.")
    try:
        validated_body = IterativeFileReaderRequestParams(**json_body)
    except Exception:
        raise BadRequest("INVALID_PARAMS")

    try:
        file_content, eof_reached = await IterativeFileReader(
            file_path=os.path.join(validated_body.repo_path, validated_body.file_path)
        ).read_lines(start_line=validated_body.start_line, end_line=validated_body.end_line)
        response = {
            "data": {
                "chunk": file_content.model_dump(mode="json"),
                "eof_reached": eof_reached,
            },
        }
        return HTTPResponse(body=json.dumps(response))
    except ValueError as ve:
        raise ValueError(ve)
    except Exception as e:
        raise ServerError(e)

