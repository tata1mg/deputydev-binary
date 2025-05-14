import json
import traceback

from sanic import Blueprint, HTTPResponse
from sanic.request import Request

from deputydev_core.services.tools.focussed_snippet_search.dataclass.main import (
    FocussedSnippetSearchParams,
)
from deputydev_core.services.tools.focussed_snippet_search.dataclass.main import FocusChunksParams

from deputydev_core.services.tools.relevant_chunks.dataclass.main import RelevantChunksParams
from app.models.dtos.update_vector_store_params import UpdateVectorStoreParams
from app.services.batch_chunk_search_service import BatchSearchService
from app.services.initialization_service import InitializationService
from app.services.relevant_chunk_service import RelevantChunksService
from app.utils.request_handlers import request_handler

chunks = Blueprint("chunks", url_prefix="")

@chunks.websocket("/relevant_chunks")
@request_handler
async def relevant_chunks(request, ws):
    try:
        data = await ws.recv()
        payload = json.loads(data)
        payload = RelevantChunksParams(**payload)
        relevant_chunks_data = await RelevantChunksService(payload.repo_path).get_relevant_chunks(payload)
        relevant_chunks_data = json.dumps(relevant_chunks_data)
        await ws.send(relevant_chunks_data)
    except Exception:
        await ws.send(
            json.dumps(
                {
                    "error": "can not find relevant chunks",
                    "message": str(traceback.format_exc()),
                }
            )
        )
        print(traceback.format_exc())


@chunks.route("/get-focus-chunks", methods=["POST"])
@request_handler
async def focus_chunks(_request: Request):
    try:
        payload = _request.json
        payload = FocusChunksParams(**payload)
        focus_chunks = await RelevantChunksService(payload.repo_path).get_focus_chunks(payload)
        return HTTPResponse(body=json.dumps(focus_chunks))
    except Exception:
        print(traceback.format_exc())
        raise Exception(traceback.format_exc())


@chunks.websocket("/update_chunks")
@request_handler
async def update_vector_store(request, ws):
    try:
        data = await ws.recv()
        payload = json.loads(data)
        payload = UpdateVectorStoreParams(**payload)

        async def progress_callback(progress):
            """Sends progress updates to the WebSocket."""
            await ws.send(
                json.dumps(
                    {
                        "status": "In Progress",
                        "repo_path": payload.repo_path,
                        "progress": progress,
                    }
                )
            )

        await InitializationService.update_chunks(payload, progress_callback)
        await ws.send(json.dumps({"status": "Completed", "repo_path": payload.repo_path, "progress": 100}))

    except Exception:
        print(traceback.format_exc())
        await ws.send(json.dumps({"status": "Failed", "message": traceback.format_exc()}))


@chunks.route("/batch_chunks_search", methods=["POST"])
async def get_autocomplete_keyword_type_chunks(_request: Request):
    payload = _request.json
    payload = FocussedSnippetSearchParams(**payload)
    chunks = await BatchSearchService.search_code(payload)
    return HTTPResponse(body=json.dumps(chunks))
