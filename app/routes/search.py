import json

from deputydev_core.services.tools.file_path_search.dataclass.main import (
    FilePathSearchPayload,
)
from deputydev_core.services.tools.file_path_search.file_path_search import (
    FilePathSearch,
)
from deputydev_core.services.tools.grep_search.dataclass.main import (
    GrepSearchRequestParams,
)
from deputydev_core.services.tools.grep_search.ripgrep_search import GrepSearch
from sanic import Blueprint, HTTPResponse
from sanic.exceptions import BadRequest
from sanic.request import Request

from app.dataclasses.codebase_search.focus_items_search.focus_items_search_dataclasses import (
    FocusSearchParams,
)
from app.services.codebase_search.focus_items_search.focus_items_search_service import (
    FocusSearchService,
)
from app.utils.ripgrep_path import get_rg_path
from app.utils.route_error_handler.error_type_handlers.tool_handler import ToolErrorHandler
from app.utils.route_error_handler.route_error_handler import get_error_handler

focus_search = Blueprint("focus_search", url_prefix="")


@focus_search.route("/get-focus-search-results", methods=["POST"], name="get_focus_search_results")
async def get_focus_search_results(_request: Request) -> HTTPResponse:
    json_body = _request.json
    chunks = await FocusSearchService.get_search_results(payload=FocusSearchParams(**json_body))
    response = {
        "data": [chunk.model_dump(mode="json") for chunk in chunks],
    }
    return HTTPResponse(body=json.dumps(response))


@focus_search.route("/get-files-in-dir", methods=["POST"], name="get_files_in_dir")
@get_error_handler(special_handlers=[ToolErrorHandler])
async def get_files_in_dir(_request: Request) -> HTTPResponse:
    json_body = _request.json
    if not json_body:
        raise BadRequest("Request payload is missing or invalid.")
    payload = FilePathSearchPayload(**json_body)
    files = FilePathSearch(repo_path=payload.repo_path).list_files(
        directory=payload.directory,
        search_terms=payload.search_terms,
    )
    response = {
        "data": files,
    }
    return HTTPResponse(body=json.dumps(response))


@focus_search.route("/grep-search", methods=["POST"], name="grep_search")
@get_error_handler(special_handlers=[ToolErrorHandler])
async def grep_search(_request: Request) -> HTTPResponse:
    json_body = _request.json
    if not json_body:
        raise BadRequest("Request payload is missing or invalid.")
    validated_body = GrepSearchRequestParams(**json_body)
    ripgrep_path = get_rg_path()
    if not ripgrep_path:
        raise BadRequest("Ripgrep path is not configured.")
    grep_search_results = await GrepSearch(
        repo_path=validated_body.repo_path, ripgrep_path=ripgrep_path
    ).perform_grep_search(
        directory_path=validated_body.directory_path,
        search_term=validated_body.search_term,
        case_insensitive=validated_body.case_insensitive,
        use_regex=validated_body.use_regex,
    )
    response = {
        "data": [
            {
                "chunk_info": chunk["chunk_info"].model_dump(mode="json"),  # type: ignore
                "matched_line": chunk["matched_line"],
            }
            for chunk in grep_search_results
        ],
        "search_term": validated_body.search_term,
        "directory_path": validated_body.directory_path,
        "case_insensitive": validated_body.case_insensitive,
        "use_regex": validated_body.use_regex,
    }
    return HTTPResponse(body=json.dumps(response))
