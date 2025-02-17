from sanic import Blueprint, Request

auth_token = Blueprint("auth_token", url_prefix="auth")


@auth_token.route("/store_token", methods=["POST"])
async def store_token(_request: Request, **kwargs):
    pass
