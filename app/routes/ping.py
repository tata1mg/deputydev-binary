from sanic import Blueprint, Request, HTTPResponse
import json

ping = Blueprint("ping", url_prefix="")


@ping.route("/ping", methods=["GET"])
async def ping_pong(_request: Request, **kwargs):
    return HTTPResponse(body=json.dumps({"ping": "pong"}))
