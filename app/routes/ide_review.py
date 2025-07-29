from typing import Union

from pydantic_core._pydantic_core import ValidationError
from sanic import Blueprint, Request
from sanic.exceptions import ServerError
from sanic.response import HTTPResponse, JSONResponse, json

from app.models.dtos.code_review_dtos.comment_validity_dto import CommentValidityParams
from app.services.comment_validator import CommentValidator
from app.services.review.dataclass.main import ReviewRequest
from app.services.review.review_service import ReviewService
from app.utils.util import flatten_multidict

review = Blueprint("review", url_prefix="")


@review.route("review/summary", methods=["GET"])
async def get_diff_summary(_request: Request) -> JSONResponse:
    """
    Get diff summary for a given repo path and target branch
    """
    try:
        data = ReviewRequest(**flatten_multidict(_request.args))
    except ValidationError as e:
        return json({"error": e.errors()}, status=400)

    response = await ReviewService.get_diff_summary(data.repo_path, data.target_branch, data.review_type)
    return json(response.model_dump(mode="json"))


@review.route("/branches/get_source_branch", methods=["GET"])
async def get_source_branch(_request: Request) -> JSONResponse:
    """
    Get source branch for a given repo path
    """
    repo_path = _request.args.get("repo_path")
    response = await ReviewService.get_source_branch(repo_path=repo_path)
    return json(response.model_dump())


@review.route("/branches/all", methods=["GET"])
async def search_branches(_request: Request) -> JSONResponse:
    """
    Search branches for a given repo path and keyword
    """
    repo_path = _request.args.get("repo_path")
    keyword = _request.args.get("keyword")
    response = await ReviewService.search_branches(repo_path=repo_path, keyword=keyword)
    return json(response.model_dump())


@review.route("/review/snapshot", methods=["POST"])
async def take_snapshot(_request: Request) -> JSONResponse:
    """
    Take snapshot for a given repo path and target branch
    """
    data = ReviewRequest(**flatten_multidict(_request.args))
    response = await ReviewService.take_snapshot(
        repo_path=data.repo_path, review_type=data.review_type, target_branch=data.target_branch
    )
    return json(response.model_dump())


@review.route("/review/reset", methods=["POST"])
async def reset(_request: Request) -> JSONResponse:
    """
    Reset review for a given repo path and target branch
    """
    data = ReviewRequest(**flatten_multidict(_request.args))
    response = await ReviewService.reset(
        repo_path=data.repo_path, review_type=data.review_type, target_branch=data.target_branch
    )
    return json(response.model_dump())


@review.route("/check-comment-validity", methods=["POST"])
async def check_comment_validity(_request: Request) -> Union[HTTPResponse, ServerError]:
    """
    Check comment validity for a given comment
    """
    params = CommentValidityParams(**_request.json)
    try:
        result = await CommentValidator().is_comment_applicable(params)
        return HTTPResponse(body=json.dumps(result))
    except Exception as e: # type: ignore
        raise ServerError(str(e))
