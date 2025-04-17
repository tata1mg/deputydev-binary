import json

from sanic import Blueprint, HTTPResponse, Request
from app.models.dtos.url_reader_params import UrlReaderParams
from app.services.url_reader.url_reader_service import UrlReaderService

url_reader = Blueprint("url_reader", url_prefix="")


@url_reader.route("/url_reader", methods=["POST"])
async def read_url(_request: Request, **kwargs):
    payload = _request.json
    payload = UrlReaderParams(**payload)
    content = await UrlReaderService().read_urls(payload)
    return HTTPResponse(body=json.dumps(content))
