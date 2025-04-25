from typing import Any
from sanic import Blueprint, Request, response

from app.dataclasses.diff_applicator.diff_applicator_dataclass import DiffApplicatorInput
from app.services.diff_applicator_service import DiffApplicatorService

diff_applicator = Blueprint("diff_applicator", url_prefix="diff-applicator")


@diff_applicator.route("/apply-diff", methods=["POST"])
async def apply_unified_diff(_request: Request, **kwargs: Any):
    data = DiffApplicatorInput(**_request.json)

    try:
        data = await DiffApplicatorService().apply_diff(data.diff_application_requests)
        return response.json(dict(
            diff_application_results=[resp.model_dump(mode="json") for resp in data]
        ), status=200)
    except Exception as e:
        return response.json({"error": str(e)}, status=500)
