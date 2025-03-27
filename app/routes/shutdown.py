from sanic import Blueprint, Sanic, response

shutdown = Blueprint("shutdown", url_prefix="")


@shutdown.get("/shutdown")
async def shutdown_server(request):
    app = Sanic.get_app()
    app.stop()
    return response.text("Server shutting down...")
