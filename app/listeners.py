from app.utils.constants import ListenerEventTypes, CONFIG_PATH
from deputydev_core.utils.constants.enums import SharedMemoryKeys
from deputydev_core.utils.shared_memory import SharedMemory


async def close_server(app, _):
    if hasattr(app.ctx, "weaviate_client"):
        await app.ctx.weaviate_client.async_client.close()
        app.ctx.weaviate_client.sync_client.close()
    # SharedMemory.delete(SharedMemoryKeys.BINARY_CONFIG.value)


listeners = [
    (close_server, ListenerEventTypes.BEFORE_SERVER_STOP.value),
]
