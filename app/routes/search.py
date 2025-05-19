import json

from app.utils.error_handler import error_handler
from sanic import Blueprint, HTTPResponse
from sanic.request import Request

from app.dataclasses.codebase_search.focus_items_search.focus_items_search_dataclasses import (
    FocusSearchParams,
)
from deputydev_core.services.tools.file_path_search.dataclass.main import (
    FilePathSearchPayload,
)
from deputydev_core.services.tools.file_path_search.file_path_search import (
    FilePathSearch,
)

from deputydev_core.services.tools.grep_search.grep_search import GrepSearch as CoreGrepSearchService
from deputydev_core.services.tools.grep_search.dataclass.main import (
    GrepSearchRequestParams,
)
from app.services.codebase_search.focus_items_search.focus_items_search_service import (
    FocusSearchService,
)
from sanic.exceptions import BadRequest, ServerError

focus_search = Blueprint("focus_search", url_prefix="")


@focus_search.route("/get-focus-search-results", methods=["POST"])
async def get_focus_search_results(_request: Request):
    json_body = _request.json
    chunks = await FocusSearchService.get_search_results(payload=FocusSearchParams(**json_body))
    response = {
        "data": [chunk.model_dump(mode="json") for chunk in chunks],
    }
    return HTTPResponse(body=json.dumps(response))


@focus_search.route("/get-files-in-dir", methods=["POST"])
@error_handler
async def get_files_in_dir(_request: Request):
    json_body = _request.json
    if not json_body:
        raise BadRequest("Request payload is missing or invalid.")
    try:
        payload = FilePathSearchPayload(**json_body)
    except Exception:
        raise BadRequest("INVALID_PARAMS")
    try:
        files = FilePathSearch(repo_path=payload.repo_path).list_files(
            directory=payload.directory,
            search_terms=payload.search_terms,
        )
        response = {
            "data": files,
        }
        return HTTPResponse(body=json.dumps(response))
    except Exception as e:
        raise ServerError(e)


@focus_search.route("/grep-search", methods=["POST"])
@error_handler
async def grep_search(_request: Request):
    json_body = _request.json
    if not json_body:
        raise BadRequest("Request payload is missing or invalid.")
    try:
        validated_body = GrepSearchRequestParams(**json_body)
    except Exception:
        raise BadRequest("INVALID_PARAMS")
    try:
        grep_search_results = await CoreGrepSearchService(repo_path=validated_body.repo_path).perform_grep_search(
            directory_path=validated_body.directory_path,
            search_terms=validated_body.search_terms,
        )

        response = {
            "data": [
                {
                    "chunk_info": chunk["chunk_info"].model_dump(mode="json"),  # type: ignore
                    "matched_line": chunk["matched_line"],
                }
                for chunk in grep_search_results
            ],
        }
        return HTTPResponse(body=json.dumps(response))
    except Exception as e:
        raise ServerError(e)
