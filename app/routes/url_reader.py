import json

from sanic import Blueprint, HTTPResponse, Request
from app.models.dtos.url_dtos.url_reader_params import UrlReaderParams
from app.models.dtos.url_dtos.save_url_params import SaveUrlParams
from app.services.url_service.url_service import UrlService

url_reader = Blueprint("url_reader", url_prefix="")


@url_reader.route("/read_url", methods=["POST"])
async def read_url(_request: Request, **kwargs):
    payload = _request.json
    payload = UrlReaderParams(**payload)
    content = await UrlService().fetch_urls_content(payload)
    return HTTPResponse(body=json.dumps(content))


@url_reader.route("/save_url", methods=["POST"])
async def save_url(_request: Request, **kwargs):
    payload = _request.json
    payload = SaveUrlParams(**payload)
    await UrlService().save_url(payload)
    return HTTPResponse(body="succesfully saved")
