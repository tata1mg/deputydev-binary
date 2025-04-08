import json
import os

from sanic import Blueprint, HTTPResponse, Request
from sanic.request import Request


from app.dataclasses.codebase_read.iterative_file_reader.iterative_file_reader_dataclass import (
    IterativeFileReaderRequestParams,
)

from app.services.codebase_read.iterative_file_reader.iterative_file_reader import (
    IterativeFileReader,
)

codebase_read = Blueprint("codebase_read", url_prefix="")


@codebase_read.route("/iteratively-read-file", methods=["POST"])
async def read_file(_request: Request):
    json_body = _request.json
    validated_body = IterativeFileReaderRequestParams(**json_body)
    file_content = await IterativeFileReader(
        file_path=os.path.join(validated_body.repo_path, validated_body.file_path)
    ).read_lines(offset_line=validated_body.offset_line)
    response = {
        "data": file_content,
    }
    return HTTPResponse(body=json.dumps(response))

