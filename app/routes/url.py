import json
from sanic import Blueprint, HTTPResponse, Request
from app.models.dtos.url_dtos.url_reader_params import UrlReaderParams
from app.models.dtos.url_dtos.search_url_params import SearchUrlParams
from app.models.dtos.url_dtos.save_url_params import SaveUrlParams
from app.models.dtos.url_dtos.update_url_params import UpdateUrlParams
from app.models.dtos.url_dtos.list_url_params import ListUrlParams
from app.services.url_service.url_service import UrlService
from app.utils.request_handlers import request_handler
from app.utils.util import parse_request_params

url_reader = Blueprint("url_reader", url_prefix="")


@url_reader.route("/read_urls", methods=["POST"])
@request_handler
async def read_url(_request: Request, **kwargs):
    payload = _request.json
    payload = UrlReaderParams(**payload)
    content = await UrlService().fetch_urls_content(payload)
    return HTTPResponse(body=json.dumps(content))


# TODO: remove index url method and reuse saved_url
async def save_url_or_index_url(_request: Request, **kwargs):
    payload = _request.json
    payload = SaveUrlParams(**payload)
    url = await UrlService().save_url(payload)
    return HTTPResponse(body=json.dumps(url))


@url_reader.route("/saved_url", methods=["POST"])
@request_handler
async def save_url(_request: Request, **kwargs):
    return await save_url_or_index_url(_request, **kwargs)


@url_reader.route("/index_url", methods=["POST"])
@request_handler
async def index_url(_request: Request, **kwargs):
    return await save_url_or_index_url(_request, **kwargs)


@url_reader.route("/saved_url", methods=["PUT"])
@request_handler
async def update_url(_request: Request, **kwargs):
    payload = _request.json
    payload = UpdateUrlParams(**payload)
    url = await UrlService().update_url(payload)
    return HTTPResponse(body=json.dumps(url))


@url_reader.route("/search_url", methods=["GET"])
@request_handler
async def search(_request: Request, **kwargs):
    query_params = parse_request_params(_request)
    payload = SearchUrlParams(**query_params)
    search_results = await UrlService().search_url(payload)
    return HTTPResponse(body=json.dumps(search_results))


@url_reader.route("/saved_url/delete", methods=["GET"])
@request_handler
async def delete(_request: Request, **kwargs):
    query_params = parse_request_params(_request)
    url_id = int(query_params.get("id"))
    await UrlService().delete_url(url_id)
    result = {"status": "deleted"}
    return HTTPResponse(body=json.dumps(result))


@url_reader.route("/saved_url/list", methods=["GET"])
@request_handler
async def list_urls(_request: Request, **kwargs):
    query_params = parse_request_params(_request)
    params = ListUrlParams(**query_params)
    urls = await UrlService().list_urls(params)
    return HTTPResponse(body=json.dumps(urls))
