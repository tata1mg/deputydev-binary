from sanic import Blueprint, Request, response

from app.services.diff_applicator_service import DiffApplicatorService

diff_applicator = Blueprint("diff_applicator", url_prefix="diff-applicator")


@diff_applicator.route("/apply-unified-diff", methods=["POST"])
async def apply_unified_diff(_request: Request, **kwargs):
    body = _request.json
    repo_path = body.get("repo_path")
    file_path_to_diff_map = body.get("file_path_to_diff_map")

    try:
        data = DiffApplicatorService().apply_diff(repo_path, file_path_to_diff_map)
        return response.json(data, status=200)
    except Exception as e:
        return response.json({"error": str(e)}, status=500)
