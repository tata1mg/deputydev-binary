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
from deputydev_core.services.tools.grep_search.grep_search import GrepSearch as CoreGrepSearchService
from sanic import Blueprint, HTTPResponse
from sanic.exceptions import BadRequest, ServerError
from sanic.request import Request

from app.dataclasses.codebase_search.focus_items_search.focus_items_search_dataclasses import (
    FocusSearchParams,
)
from app.services.codebase_search.focus_items_search.focus_items_search_service import (
    FocusSearchService,
)
from app.utils.route_error_handler.error_type_handlers.tool_handler import ToolErrorHandler
from app.utils.route_error_handler.route_error_handler import get_error_handler

focus_search = Blueprint("focus_search", url_prefix="")


@focus_search.route("/get-focus-search-results", methods=["POST"])
async def get_focus_search_results(_request: Request) -> HTTPResponse:
    json_body = _request.json
    chunks = await FocusSearchService.get_search_results(payload=FocusSearchParams(**json_body))
    response = {
        "data": [chunk.model_dump(mode="json") for chunk in chunks],
    }
    return HTTPResponse(body=json.dumps(response))


@focus_search.route("/get-files-in-dir", methods=["POST"])
@get_error_handler(special_handlers=[ToolErrorHandler])
async def get_files_in_dir(_request: Request) -> HTTPResponse:
    json_body = _request.json
    if not json_body:
        raise BadRequest("Request payload is missing or invalid.")
    try:
        payload = FilePathSearchPayload(**json_body)
    except Exception:  # noqa: BLE001
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
    except Exception as e:  # noqa: BLE001
        raise ServerError(e)


@focus_search.route("/grep-search", methods=["POST"])
@get_error_handler(special_handlers=[ToolErrorHandler])
async def grep_search(_request: Request) -> HTTPResponse:
    json_body = _request.json
    if not json_body:
        raise BadRequest("Request payload is missing or invalid.")
    try:
        validated_body = GrepSearchRequestParams(**json_body)
    except Exception:  # noqa: BLE001
        raise BadRequest("INVALID_PARAMS")
    grep_search_results = await CoreGrepSearchService(repo_path=validated_body.repo_path).perform_grep_search(
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
    }
    return HTTPResponse(body=json.dumps(response))
