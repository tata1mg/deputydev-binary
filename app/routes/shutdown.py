from sanic import Blueprint, response, Sanic

shutdown = Blueprint("shutdown", url_prefix="")


@shutdown.get("/shutdown")
async def shutdown_server(request):
    app = Sanic.get_app()
    app.stop()
    return response.text("Server shutting down...")
