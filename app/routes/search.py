import json
from sanic import Blueprint, Request, HTTPResponse
from sanic.request import Request
from app.dataclasses.codebase_search.file_path_search.file_path_search_dataclasses import (
    FilePathSearchPayload,
)
from app.services.codebase_search.focus_items_search.focus_items_search_service import (
    FocusSearchService,
)
from app.services.codebase_search.file_path_search.file_path_search_service import (
    FilePathSearchService,
)
from app.dataclasses.codebase_search.focus_items_search.focus_items_search_dataclasses import (
    FocusSearchParams,
)

focus_search = Blueprint("focus_search", url_prefix="")


@focus_search.route("/get-focus-search-results", methods=["POST"])
async def get_focus_search_results(_request: Request):
    json_body = _request.json
    chunks = await FocusSearchService.get_search_results(
        payload=FocusSearchParams(**json_body)
    )
    response = {
        "data": [chunk.model_dump(mode="json") for chunk in chunks],
    }
    print(response)
    return HTTPResponse(body=json.dumps(response))


@focus_search.route("/get-files-in-dir", methods=["POST"])
async def get_files_in_dir(_request: Request):
    json_body = _request.json
    payload = FilePathSearchPayload(**json_body)
    files = FilePathSearchService(repo_path=payload.repo_path).list_files(
        directory=payload.directory,
        search_terms=payload.search_terms,
    )
    response = {
        "data": files,
    }
    print(response)
    return HTTPResponse(body=json.dumps(response))
