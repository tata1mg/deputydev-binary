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
from sanic.exceptions import ServerError, BadRequest
url_reader = Blueprint("url_reader", url_prefix="")


@url_reader.route("/read_urls", methods=["POST"])
@request_handler
async def read_url(_request: Request, **kwargs):
    try:
        payload = _request.json
        if not payload:
            raise BadRequest("Request payload is missing or invalid.")
        payload = UrlReaderParams(**payload)
        content = await UrlService().fetch_urls_content(payload)
        return HTTPResponse(body=json.dumps(content))
    except Exception as e:
        raise ServerError(f"Failed to read URLs: {str(e)}")


async def save_url_or_index_url(_request: Request, **kwargs):
    try:
        payload = _request.json
        if not payload:
            raise BadRequest("Request payload is missing or invalid.")
        payload = SaveUrlParams(**payload)
        url = await UrlService().save_url(payload)
        return HTTPResponse(body=json.dumps(url))
    except Exception as e:
        raise ServerError(f"Failed to save URL: {str(e)}")


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
    try:
        payload = _request.json
        if not payload:
            raise BadRequest("Request payload is missing or invalid.")
        payload = UpdateUrlParams(**payload)
        url = await UrlService().update_url(payload)
        return HTTPResponse(body=json.dumps(url))
    except Exception as e:
        raise ServerError(f"Failed to update URL: {str(e)}")


@url_reader.route("/search_url", methods=["GET"])
@request_handler
async def search(_request: Request, **kwargs):
    try:
        query_params = parse_request_params(_request)
        if not query_params:
            raise BadRequest("Missing query parameters.")
        payload = SearchUrlParams(**query_params)
        search_results = await UrlService().search_url(payload)
        return HTTPResponse(body=json.dumps(search_results))
    except Exception as e:
        raise ServerError(f"Failed to search URL: {str(e)}")


@url_reader.route("/saved_url/delete", methods=["GET"])
@request_handler
async def delete(_request: Request, **kwargs):
    try:
        query_params = parse_request_params(_request)
        url_id = query_params.get("id")
        if not url_id:
            raise BadRequest("Missing 'id' parameter.")
        await UrlService().delete_url(int(url_id))
        result = {"status": "deleted"}
        return HTTPResponse(body=json.dumps(result))
    except ValueError:
        raise BadRequest("Invalid 'id' parameter, must be an integer.")
    except Exception as e:
        raise ServerError(f"Failed to delete URL: {str(e)}")


@url_reader.route("/saved_url/list", methods=["GET"])
@request_handler
async def list_urls(_request: Request, **kwargs):
    try:
        query_params = parse_request_params(_request)
        params = ListUrlParams(**query_params)
        urls = await UrlService().list_urls(params)
        return HTTPResponse(body=json.dumps(urls))
    except Exception as e:
        raise ServerError(f"Failed to list URLs: {str(e)}")