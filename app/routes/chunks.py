import json
from sanic import Blueprint, Request, HTTPResponse
from sanic.request import Request
from app.models.dtos.relevant_chunks_params import RelevantChunksParams
from app.models.dtos.update_vector_store_params import UpdateVectorStoreParams
from app.services.batch_chunk_search_service import BatchSearchService
from app.services.initialization_service import InitializationService
from app.services.relevant_chunk_service import RelevantChunksService
from app.models.dtos.batch_chunk_search_params import BatchSearchParams
from app.services.autocomplete_search_service import AutocompleteSearchService
from app.models.dtos.autocomplete_search_params import AutocompleteSearchParams

chunks = Blueprint("chunks", url_prefix="")


@chunks.websocket("/relevant_chunks")
async def relevant_chunks(request, ws):
    try:
        data = await ws.recv()
        payload = json.loads(data)
        payload = RelevantChunksParams(**payload)
        relevant_chunks_data = await RelevantChunksService(
            payload.auth_token, payload.repo_path
        ).get_relevant_chunks(payload)
        relevant_chunks_data = json.dumps(relevant_chunks_data)
        await ws.send(relevant_chunks_data)
    except Exception as e:
        await ws.send(json.dumps({"error": "can not find relevant chunks"}))
        # uncomment for local debugging
        # import traceback
        # print(traceback.format_exc())
        print(f"Connection closed: {e}")


@chunks.websocket("/update_chunks")
async def update_vector_store(request, ws):
    try:
        data = await ws.recv()
        payload = json.loads(data)
        payload = UpdateVectorStoreParams(**payload)

        async def progress_callback(progress):
            """Sends progress updates to the WebSocket."""
            await ws.send(json.dumps({"status": "In Progress", "progress": progress}))

        await InitializationService.update_vector_store(payload, progress_callback)
        await ws.send(json.dumps({"status": "Completed", "progress": 100}))

    except Exception as e:
        # uncomment for local debugging
        # print(traceback.format_exc())
        await ws.send(json.dumps({"status": "Failed"}))
        print(f"Connection closed: {e}")


@chunks.route("/keyword_search", methods=["POST"])
async def get_autocomplete_keyword_chunks(_request: Request, **kwargs):
    payload = _request.json
    headers = _request.headers
    payload = AutocompleteSearchParams(**payload)
    chunks = await AutocompleteSearchService.get_autocomplete_keyword_chunks(payload)
    return HTTPResponse(body=json.dumps(chunks))


@chunks.route("/keyword_type_search", methods=["POST"])
async def get_autocomplete_keyword_type_chunks(_request: Request):
    payload = _request.json
    payload = AutocompleteSearchParams(**payload)
    chunks = await AutocompleteSearchService.get_autocomplete_keyword_type_chunks(
        payload
    )
    return HTTPResponse(body=json.dumps(chunks))


@chunks.route("/update_chunks", methods=["POST"])
async def update_vector_store(request):
    try:
        payload = request.json
        payload = UpdateVectorStoreParams(**payload)
        await InitializationService.initialize(payload)
        return HTTPResponse(body=json.dumps({}))
    except Exception as e:
        # uncomment for local debugging
        # print(traceback.format_exc())
        raise e
        # print(f"Connection closed: {e}")


@chunks.route("/batch_chunks_search", methods=["POST"])
async def get_autocomplete_keyword_type_chunks(_request: Request):
    payload = _request.json
    payload = BatchSearchParams(**payload)
    chunks = await BatchSearchService.search_code(
        payload
    )
    return HTTPResponse(body=json.dumps(chunks))
