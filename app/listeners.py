from app.utils.constants import (
    ListenerEventTypes,
    WEAVIATE_HOST,
    WEAVIATE_GRPC_PORT,
    WEAVIATE_HTTP_PORT,
)

from deputydev_core.utils.config_manager import ConfigManager
from deputydev_core.services.initialization.initialization_service import (
    InitializationManager,
)


async def setup_weaviate(app, _):
    ConfigManager.in_memory = True
    ConfigManager.set(
        {
            "WEAVIATE_HOST": WEAVIATE_HOST,
            "WEAVIATE_GRPC_PORT": WEAVIATE_GRPC_PORT,
            "WEAVIATE_HTTP_PORT": WEAVIATE_HTTP_PORT,
        }
    )
    weaviate_client = await InitializationManager().initialize_vector_db()
    app.ctx.weaviate_client = weaviate_client


async def close_weaviate(app, _):
    await app.ctx.weaviate_client.async_client.close()
    app.ctx.weaviate_client.sync_client.close()


listeners = [
    (setup_weaviate, ListenerEventTypes.BEFORE_SERVER_START.value),
    (close_weaviate, ListenerEventTypes.BEFORE_SERVER_STOP.value),
]
