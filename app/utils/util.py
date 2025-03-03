from typing import Dict, List

from deputydev_core.services.chunking.chunk_info import ChunkInfo
from sanic import Sanic


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
        weaviate_clients = app.ctx.weaviate_client
        try:
            if (
                await weaviate_clients.async_client.schema.get()
                and weaviate_clients.sync_client.schema.get()
            ):
                return weaviate_clients
        except Exception as error:
            print(f"Connection was dropped, Reconnecting {error}")
            weaviate_clients.sync_client.connect()
            await weaviate_clients.async_client.connect()
            return weaviate_clients
