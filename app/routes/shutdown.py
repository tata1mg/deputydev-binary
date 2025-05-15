from sanic import Blueprint, Sanic, response
import asyncio

shutdown = Blueprint("shutdown", url_prefix="")


@shutdown.get("/shutdown")
async def shutdown_server(request):
    app = Sanic.get_app()

    # close the weaviate client if it exists
    if hasattr(app.ctx, "weaviate_client"):
        weaviate_client = app.ctx.weaviate_client
        if weaviate_client:
            await weaviate_client.async_client.close()
            weaviate_client.sync_client.close()

    # kill the weaviate process if it exists
    if hasattr(app.ctx, "weaviate_process"):
        weaviate_process: asyncio.subprocess.Process = app.ctx.weaviate_process
        if weaviate_process:
            weaviate_process.terminate()
            await weaviate_process.wait()

    app.stop()
    return response.text("Server shutting down...")
