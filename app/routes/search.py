import json
from sanic import Blueprint, Request, HTTPResponse
from sanic.request import Request
from app.services.focus_search.focus_search_service import FocusSearchService
from app.dataclasses.focus_search.focus_search_dataclasses import FocusSearchParams

focus_search = Blueprint("focus_search", url_prefix="")


@focus_search.route("/get-focus-search-results", methods=["POST"])
async def get_autocomplete_keyword_type_chunks(_request: Request):
    json_body = _request.json
    chunks = await FocusSearchService.get_search_results(
        payload=FocusSearchParams(**json_body)
    )
    response = {
        "data": [chunk.model_dump(mode="json") for chunk in chunks],
    }
    print(response)
    return HTTPResponse(body=json.dumps(response))
