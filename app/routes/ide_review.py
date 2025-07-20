from pydantic_core._pydantic_core import ValidationError
from sanic import Blueprint, Request
from sanic.response import json
from app.services.review.review_service import ReviewService
from app.utils.util import flatten_multidict
from app.services.review.dataclass.main import ReviewRequest

review = Blueprint("review", url_prefix="")


@review.route("review/new", methods=["GET"])
async def server_sync(_request: Request):
    try:
        data = ReviewRequest(**flatten_multidict(_request.args))
    except ValidationError as e:
        return json({"error": e.errors()}, status=400)

    response = await ReviewService.get_diff_summary(data.repo_path, data.target_branch, data.review_type)
    return json(response.model_dump(mode="json"))


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


@review.route("/review/start", methods=["POST"])
async def server_sync(_request: Request):
    data = ReviewRequest(**flatten_multidict(_request.args))
    response = await ReviewService.start_review(repo_path=data.repo_path, review_type=data.review_type)
    return json(response.model_dump())


@review.route("/review/reset", methods=["POST"])
async def server_sync(_request: Request):
    repo_path = _request.args.get("repo_path")
    response = await ReviewService.reset(repo_path=repo_path)
    return json(response.model_dump())