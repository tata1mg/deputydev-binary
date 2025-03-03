import json

from sanic import Blueprint

from app.models.dtos.relevant_chunks_params import RelevantChunksParams
from app.models.dtos.update_vector_store_params import UpdateVectorStoreParams
from app.services.initialization_service import InitializationService
from app.services.relevant_chunk_service import RelevantChunksService

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
        await InitializationService.initialize(payload)
        await ws.send(json.dumps({"status": "Completed"}))
    except Exception as e:
        # uncomment for local debugging
        # print(traceback.format_exc())
        await ws.send(json.dumps({"status": "Failed"}))
        print(f"Connection closed: {e}")
