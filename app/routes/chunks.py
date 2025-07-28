import asyncio
import json
import traceback
from typing import Dict, List

from deputydev_core.services.tools.focussed_snippet_search.dataclass.main import (
    DirectoryStructureParams,
    FocusChunksParams,
    FocussedSnippetSearchParams,
)
from deputydev_core.services.tools.relevant_chunks.dataclass.main import RelevantChunksParams
from deputydev_core.services.tools.relevant_chunks.relevant_chunk import RelevantChunks
from deputydev_core.utils.app_logger import AppLogger
from sanic import Blueprint, HTTPResponse, Request, Websocket
from sanic.exceptions import BadRequest

from app.models.dtos.update_vector_store_params import UpdateVectorStoreParams
from app.services.batch_chunk_search_service import BatchSearchService
from app.services.initialization_service import InitializationService
from app.services.relevant_chunk_service import RelevantChunksService
from app.utils.request_handlers import request_handler
from app.utils.route_error_handler.error_type_handlers.tool_handler import ToolErrorHandler
from app.utils.route_error_handler.route_error_handler import get_error_handler

chunks = Blueprint("chunks", url_prefix="")


@chunks.websocket("/relevant_chunks")
@request_handler
@get_error_handler(special_handlers=[])
async def relevant_chunks(request: Request, ws: Websocket) -> None:
    try:
        data = await ws.recv()
        payload = json.loads(data)
        payload = RelevantChunksParams(**payload)
        relevant_chunks_data = await RelevantChunksService(payload.repo_path).get_relevant_chunks(payload)
        relevant_chunks_data = json.dumps(relevant_chunks_data)
        await ws.send(relevant_chunks_data)
    except Exception as e:  # noqa: BLE001
        await ws.send(
            json.dumps(
                {
                    "error_code": 500,
                    "error_type": "SERVER_ERROR",
                    "error_message": f"Can not find relevant chunks due to: {str(e)}",
                    "traceback": str(traceback.format_exc()),
                }
            )
        )
        AppLogger.log_error(traceback.format_exc())


@chunks.route("/get-focus-chunks", methods=["POST"])
@request_handler
@get_error_handler(special_handlers=[])
async def focus_chunks(_request: Request) -> HTTPResponse:
    try:
        payload = _request.json
        payload = FocusChunksParams(**payload)
        focus_chunks = await RelevantChunksService(payload.repo_path).get_focus_chunks(payload)
        return HTTPResponse(body=json.dumps(focus_chunks))
    except Exception:  # noqa: BLE001
        AppLogger.log_error(traceback.format_exc())
        raise Exception(traceback.format_exc())


@chunks.route("/get-directory-structure", methods=["POST"])
@request_handler
@get_error_handler(special_handlers=[ToolErrorHandler])
async def directory_format(_request: Request) -> HTTPResponse:
    payload = _request.json
    payload = DirectoryStructureParams(**payload)
    relevant_chunks = RelevantChunks(payload.repo_path)
    directory_tree = await relevant_chunks.get_directory_structure(payload)
    return HTTPResponse(body=json.dumps(directory_tree))


@chunks.websocket("/update_chunks")
@request_handler
@get_error_handler(special_handlers=[])
async def update_vector_store(request: Request, ws: Websocket) -> None:
    try:
        data = await ws.recv()
        payload = json.loads(data)
        payload = UpdateVectorStoreParams(**payload)
        files_indexing_status = {}

        async def indexing_progress_callback(progress: float, indexing_status: List[Dict[str, str]]) -> None:
            nonlocal files_indexing_status
            """Sends progress updates to the WebSocket."""
            files_indexing_status = indexing_status
            await ws.send(
                json.dumps(
                    {
                        "task": "INDEXING",
                        "status": "IN_PROGRESS",
                        "repo_path": payload.repo_path,
                        "progress": progress,
                        "indexing_status": list(indexing_status.values()),
                    }
                )
            )

        async def embedding_progress_callback(progress: float) -> None:
            await ws.send(
                json.dumps(
                    {
                        "task": "EMBEDDING",
                        "status": "IN_PROGRESS",
                        "repo_path": payload.repo_path,
                        "progress": progress,
                    }
                )
            )

        indexing_task, embedding_task = await InitializationService.update_chunks(
            payload, indexing_progress_callback, embedding_progress_callback
        )
        indexing_done, embedding_done = False, False

        if indexing_task or embedding_task:
            while True:
                if not indexing_done and indexing_task and indexing_task.done():
                    indexing_done = True
                    await ws.send(
                        json.dumps(
                            {
                                "task": "INDEXING",
                                "status": "COMPLETED",
                                "repo_path": payload.repo_path,
                                "progress": 100,
                                "indexing_status": list(files_indexing_status.values()),
                            }
                        )
                    )
                if not embedding_done and embedding_task and embedding_task.done():
                    embedding_done = True
                    await ws.send(
                        json.dumps(
                            {
                                "task": "EMBEDDING",
                                "status": "COMPLETED",
                                "repo_path": payload.repo_path,
                                "progress": 100,
                            }
                        )
                    )
                if (not indexing_task or indexing_task.done()) and (not embedding_task or embedding_task.done()):
                    break
                await asyncio.sleep(0.5)

    except Exception:  # noqa: BLE001
        await ws.send(json.dumps({"status": "FAILED", "message": traceback.format_exc()}))


@chunks.route("/batch_chunks_search", methods=["POST"])
@get_error_handler(special_handlers=[ToolErrorHandler])
async def get_autocomplete_keyword_type_chunks(_request: Request) -> HTTPResponse:
    payload = _request.json
    if not payload:
        raise BadRequest("Request payload is missing or invalid.")
    payload = FocussedSnippetSearchParams(**payload)
    chunks = await BatchSearchService.search_code(payload)
    return HTTPResponse(body=json.dumps(chunks))
