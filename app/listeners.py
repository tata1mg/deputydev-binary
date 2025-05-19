from app.utils.constants import ListenerEventTypes

async def close_server(app, _):
    if hasattr(app.ctx, "weaviate_client"):
        await app.ctx.weaviate_client.async_client.close()
        app.ctx.weaviate_client.sync_client.close()


listeners = [
    (close_server, ListenerEventTypes.BEFORE_SERVER_STOP.value),
]
