import json

from sanic import Blueprint, HTTPResponse, Request

ping = Blueprint("ping", url_prefix="")


@ping.route("/ping", methods=["GET"])
async def ping_pong(_request: Request, **kwargs):
    return HTTPResponse(body=json.dumps({"ping": "pong"}))
