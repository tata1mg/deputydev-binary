import json
from typing import Any

from sanic import Blueprint, HTTPResponse, Request
from sanic.exceptions import BadRequest

from app.models.dtos.url_dtos.list_url_params import ListUrlParams
from app.models.dtos.url_dtos.save_url_params import SaveUrlParams
from app.models.dtos.url_dtos.search_url_params import SearchUrlParams
from app.models.dtos.url_dtos.update_url_params import UpdateUrlParams
from app.models.dtos.url_dtos.url_reader_params import UrlReaderParams
from app.services.url_service.url_service import UrlService
from app.utils.request_handlers import request_handler
from app.utils.route_error_handler.route_error_handler import get_error_handler
from app.utils.util import parse_request_params

url_reader = Blueprint("url_reader", url_prefix="")


@url_reader.route("/read_urls", methods=["POST"], name="read_urls")
@request_handler
@get_error_handler(special_handlers=[])
async def read_url(_request: Request, **kwargs: Any) -> HTTPResponse:
    payload = _request.json
    if not payload:
        raise BadRequest("Request payload is missing or invalid.")

    payload = UrlReaderParams(**payload)
    content = await UrlService().fetch_urls_content(payload, _request.headers)
    return HTTPResponse(body=json.dumps(content))


async def save_url_or_index_url(_request: Request, **kwargs: Any) -> HTTPResponse:
    payload = _request.json
    if not payload:
        raise BadRequest("Request payload is missing or invalid.")
    payload = SaveUrlParams(**payload)
    url = await UrlService().save_url(payload)
    return HTTPResponse(body=json.dumps(url))


@url_reader.route("/saved_url", methods=["POST"], name="save_url")
@request_handler
@get_error_handler(special_handlers=[])
async def save_url(_request: Request, **kwargs: Any) -> HTTPResponse:
    return await save_url_or_index_url(_request, **kwargs)


@url_reader.route("/index_url", methods=["POST"])
@request_handler
@get_error_handler(special_handlers=[])
async def index_url(_request: Request, **kwargs: Any) -> HTTPResponse:
    return await save_url_or_index_url(_request, **kwargs)


@url_reader.route("/saved_url", methods=["PUT"], name="update_url")
@request_handler
@get_error_handler(special_handlers=[])
async def update_url(_request: Request, **kwargs: Any) -> HTTPResponse:
    payload = _request.json
    if not payload:
        raise BadRequest("Request payload is missing or invalid.")
    payload = UpdateUrlParams(**payload)
    url = await UrlService().update_url(payload)
    return HTTPResponse(body=json.dumps(url))


@url_reader.route("/search_url", methods=["GET"], name="search_url")
@request_handler
@get_error_handler(special_handlers=[])
async def search(_request: Request, **kwargs: Any) -> HTTPResponse:
    query_params = parse_request_params(_request)
    if not query_params:
        raise BadRequest("Missing query parameters.")
    payload = SearchUrlParams(**query_params)
    search_results = await UrlService().search_url(payload)
    return HTTPResponse(body=json.dumps(search_results))


@url_reader.route("/saved_url/delete", methods=["GET"], name="delete_url")
@request_handler
@get_error_handler(special_handlers=[])
async def delete(_request: Request, **kwargs: Any) -> HTTPResponse:
    query_params = parse_request_params(_request)
    url_id = query_params.get("id")
    if not url_id:
        raise BadRequest("Missing 'id' parameter.")
    await UrlService().delete_url(int(url_id))
    result = {"status": "deleted"}
    return HTTPResponse(body=json.dumps(result))


@url_reader.route("/saved_url/list", methods=["GET"], name="list_urls")
@request_handler
@get_error_handler(special_handlers=[])
async def list_urls(_request: Request, **kwargs: Any) -> HTTPResponse:
    query_params = parse_request_params(_request)
    params = ListUrlParams(**query_params)
    urls = await UrlService().list_urls(params)
    return HTTPResponse(body=json.dumps(urls))
