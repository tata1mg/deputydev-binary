from sanic import Blueprint, Request

from app.services.diff_applicator_service import DiffApplicatorService
from sanic import response

diff_applicator = Blueprint("diff_applicator", url_prefix="diff-applicator")


@diff_applicator.route("/apply-unified-diff", methods=["POST"])
async def apply_unified_diff(_request: Request, **kwargs):
    body = _request.json
    repo_path = body.get("repo_path")
    file_path_to_diff_map = body.get("file_path_to_diff_map")

    try:
        DiffApplicatorService().apply_diff(repo_path, file_path_to_diff_map)
        return response.json({"message": "Unified Diff applied successfully"}, status=200)
    except Exception as e:
        return response.json({"error": str(e)}, status=500)

