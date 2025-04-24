from typing import Dict, List, TYPE_CHECKING

from deputydev_core.services.chunking.chunk_info import ChunkInfo
from deputydev_core.services.repository.dataclasses.main import (
    WeaviateSyncAndAsyncClients,
)
from deputydev_core.utils.context_vars import get_context_value
from sanic import Sanic
from sanic.request import Request
from app.utils.constants import Headers

if TYPE_CHECKING:
    from deputydev_core.services.repository.dataclasses.main import (
        WeaviateSyncAndAsyncClients,
    )
    from deputydev_core.services.initialization.initialization_service import (
        InitializationManager,
    )


def jsonify_chunks(chunks: List[ChunkInfo]) -> List[Dict[str, dict]]:
    return [chunk.model_dump(mode="json") for chunk in chunks]


def chunks_content(chunks: List[ChunkInfo]) -> List[str]:
    return [chunk.content for chunk in chunks]


def filter_chunks_by_denotation(
        chunks: List[ChunkInfo], denotations: List[str]
) -> List[ChunkInfo]:
    return [chunk for chunk in chunks if chunk.denotation in denotations]


async def weaviate_connection():
    app = Sanic.get_app()
    if app.ctx.weaviate_client:
        weaviate_clients: WeaviateSyncAndAsyncClients = app.ctx.weaviate_client
        if not weaviate_clients.async_client.is_connected():
            print(f"Async Connection was dropped, Reconnecting")
            await weaviate_clients.async_client.connect()
        if not weaviate_clients.sync_client.is_connected():
            print(f"Sync Connection was dropped, Reconnecting")
            weaviate_clients.sync_client.connect()
        return weaviate_clients


async def initialise_weaviate_client(initialization_manager: "InitializationManager") -> "WeaviateSyncAndAsyncClients":
    weaviate_client = await weaviate_connection()
    if weaviate_client:
        weaviate_client = weaviate_client
    else:
        weaviate_client = await initialization_manager.initialize_vector_db()
    return weaviate_client


def get_common_headers() -> Dict[str, str]:
    headers = get_context_value("headers")
    return {
        Headers.X_CLIENT: headers.get(Headers.X_CLIENT),
        Headers.X_Client_Version: headers.get(Headers.X_Client_Version),
    }


def parse_request_params(req: Request):
    """
    function to get all query params and match_info params as query params
    :return: a dictionary of query params
    """
    args = req.args
    params = {}
    for key, value in args.items():
        modified_key = key.replace("[]", "")
        if "[]" in key:
            params[modified_key] = value
        else:
            params[key] = value if len(value) > 1 else value[0]

    for key, value in req.match_info.items():
        params[key] = value
    return params
