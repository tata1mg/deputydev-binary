import json

from sanic import Blueprint, HTTPResponse
from sanic.request import Request

from app.dataclasses.codebase_search.file_path_search.file_path_search_dataclasses import (
    FilePathSearchPayload,
)
from app.dataclasses.codebase_search.focus_items_search.focus_items_search_dataclasses import (
    FocusSearchParams,
)
from app.dataclasses.codebase_search.grep_search.grep_search_dataclass import (
    GrepSearchRequestParams,
)
from app.services.codebase_search.file_path_search.file_path_search_service import (
    FilePathSearchService,
)
from app.services.codebase_search.focus_items_search.focus_items_search_service import (
    FocusSearchService,
)
from app.services.codebase_search.grep_search.grep_search import GrepSearchService

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
    return HTTPResponse(body=json.dumps(response))


@focus_search.route("/grep-search", methods=["POST"])
async def grep_search(_request: Request):
    json_body = _request.json
    validated_body = GrepSearchRequestParams(**json_body)
    grep_search_results = await GrepSearchService(
        repo_path=validated_body.repo_path
    ).perform_grep_search(
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
