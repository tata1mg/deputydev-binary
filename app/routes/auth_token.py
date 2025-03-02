from sanic import Blueprint, Request
from app.services.auth_token_service import AuthTokenService
from sanic import json

auth_token = Blueprint("auth_token", url_prefix="auth")


@auth_token.route("/store_token", methods=["POST"])
async def store_token(_request: Request, **kwargs):
    headers = _request.headers
    response = await AuthTokenService.store_token(headers)
    return json(response)

@auth_token.route("/load_token", methods=["GET"])
async def load_token(_request: Request, **kwargs):
    headers = _request.headers
    response = await AuthTokenService.load_token(headers)
    return json(response)
