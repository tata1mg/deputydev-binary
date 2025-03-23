from sanic import Blueprint, Request, json
from deputydev_core.utils.context_vars import get_context_value
from deputydev_core.services.auth_token_storage.auth_token_service import (
    AuthTokenService,
)
from app.utils.request_handlers import request_handler
from app.utils.constants import Headers

auth_token = Blueprint("auth_token", url_prefix="auth")


@auth_token.route("/store_token", methods=["POST"])
@request_handler
async def store_token(_request: Request, **kwargs):
    response = await AuthTokenService.store_token(
        get_context_value("headers").get(Headers.X_CLIENT)
    )
    return json(response)


@auth_token.route("/load_token", methods=["GET"])
@request_handler
async def load_token(_request: Request, **kwargs):
    response = await AuthTokenService.load_token(
        get_context_value("headers").get(Headers.X_CLIENT)
    )
    return json(response)

@auth_token.route("/delete_token", methods=["POST"])
@request_handler
async def delete_token(_request: Request, **kwargs):
    response = await AuthTokenService.delete_token(
        get_context_value("headers").get(Headers.X_CLIENT)
    )
    return json(response)
