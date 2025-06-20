import asyncio

from sanic import Blueprint, Sanic, response

shutdown = Blueprint("shutdown", url_prefix="")


@shutdown.get("/shutdown")
async def shutdown_server(request):
    app = Sanic.get_app()

    await close_weaviate_client(app)
    await stop_weaviate_process()

    app.stop()
    return response.text("Server shutting down...")


async def close_weaviate_client(app):
    # close the weaviate client if it exists
    if hasattr(app.ctx, "weaviate_client"):
        weaviate_client = app.ctx.weaviate_client
        if weaviate_client:
            await weaviate_client.async_client.close()
            weaviate_client.sync_client.close()


async def stop_weaviate_process():
    try:
        proc = await asyncio.create_subprocess_exec(
            "docker", "stop", "-t", "30", "weaviate", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
    except Exception:
        pass
