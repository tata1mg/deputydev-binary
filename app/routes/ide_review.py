from pydantic_core._pydantic_core import ValidationError
from sanic import Blueprint, Request
from sanic.response import json

from app.dataclasses.review.main import ReviewRequest
from app.services.review.review_service import ReviewService

review = Blueprint("review", url_prefix="review")


def flatten_multidict(multi: dict) -> dict:
    return {k: v[0] if isinstance(v, list) else v for k, v in multi.items()}


@review.route("/new", methods=["GET"])
async def server_sync(_request: Request):
    try:
        data = ReviewRequest(**flatten_multidict(_request.args))
    except ValidationError as e:
        return json({"error": e.errors()}, status=400)

    response = await ReviewService.get_diff_summary(data.repo_path, data.target_branch, data.review_type)
    return json(response.model_dump())


@review.route("/branches/get_source_branch", methods=["GET"])
async def server_sync(_request: Request):
    repo_path = _request.args.get("repo_path")
    response = await ReviewService.get_source_branch(repo_path=repo_path)
    return json(response.model_dump())


@review.route("/branches/all", methods=["GET"])
async def server_sync(_request: Request):
    repo_path = _request.args.get("repo_path")
    keyword = _request.args.get("keyword")
    response = await ReviewService.search_branches(repo_path=repo_path, keyword=keyword)
    return json(response.model_dump())
