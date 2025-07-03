import json
from sanic import Blueprint, HTTPResponse
from sanic.exceptions import ServerError
from sanic.request import Request
from app.models.dtos.code_review_dtos.comment_validity_dto import CommentValidityParams
from app.services.comment_validator import CommentValidator

code_review = Blueprint("code_review", url_prefix="")


@code_review.route("/check-comment-validity", methods=["POST"])
async def comment_validity(_request: Request) -> HTTPResponse:
    params = CommentValidityParams(**_request.json)
    try:
        result = await CommentValidator().is_comment_applicable(params)
        return HTTPResponse(body=json.dumps(result))
    except Exception as e:
        raise ServerError(str(e))
