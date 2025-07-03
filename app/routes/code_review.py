import json
from app.utils.read_file import read_file_lines
from sanic import Blueprint, HTTPResponse
from sanic.exceptions import ServerError
from sanic.request import Request
from app.models.dtos.code_review_dtos.comment_validity_dto import CommentValidityParams
from app.utils.util import hash_content

code_review = Blueprint("code_review", url_prefix="")

LINE_UPDATED = "The line has updated, can not apply comment"
FILE_DELETED_OR_MOVED = "The file has been moved or deleted."


@code_review.route("/check-comment-validity", methods=["POST"])
async def comment_validity(_request: Request) -> HTTPResponse:
    params = CommentValidityParams(**_request.json)
    try:
        line, _, _ = await read_file_lines("/"+params.repo_path +"/"+ params.file_path, params.line_number - 1)
        if not line:
            return HTTPResponse(body=json.dumps({"is_applicable": False, "message": LINE_UPDATED}))

        is_applicable = hash_content(line) == params.line_hash
        msg = "" if is_applicable else LINE_UPDATED
        return HTTPResponse(body=json.dumps({"is_applicable": is_applicable, "message": msg}))

    except FileNotFoundError:
        return HTTPResponse(body=json.dumps({"is_applicable": False, "message": FILE_DELETED_OR_MOVED}))

    except Exception as e:
        raise ServerError(str(e))
