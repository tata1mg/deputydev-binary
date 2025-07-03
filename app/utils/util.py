from typing import Dict, List
import hashlib
from deputydev_core.services.chunking.chunk_info import ChunkInfo
from deputydev_core.utils.constants.enums import ContextValueKeys
from deputydev_core.utils.context_value import ContextValue
from deputydev_core.utils.context_vars import get_context_value
from sanic.request import Request

from app.utils.constants import Headers


def jsonify_chunks(chunks: List[ChunkInfo]) -> List[Dict[str, dict]]:
    return [chunk.model_dump(mode="json") for chunk in chunks]


def chunks_content(chunks: List[ChunkInfo]) -> List[str]:
    return [chunk.content for chunk in chunks]


def filter_chunks_by_denotation(chunks: List[ChunkInfo], denotations: List[str]) -> List[ChunkInfo]:
    return [chunk for chunk in chunks if chunk.denotation in denotations]


def get_extension_auth_token() -> str | None:
    return ContextValue.get(ContextValueKeys.EXTENSION_AUTH_TOKEN.value)


def get_common_headers(add_auth: bool = False) -> Dict[str, str]:
    headers = get_context_value("headers")
    formatted_headers = {
        Headers.X_CLIENT: headers.get(Headers.X_CLIENT),
        Headers.X_Client_Version: headers.get(Headers.X_Client_Version),
    }
    if add_auth:
        formatted_headers[Headers.AUTHORIZATION] = f"Bearer {get_extension_auth_token()}"
    return formatted_headers


def parse_request_params(req: Request) -> Dict[str, str]:
    """
    function to get all query params and match_info params as query params
    :return: a dictionary of query params
    """
    args = req.args
    params: Dict[str, str] = {}
    for key, value in args.items():
        modified_key = key.replace("[]", "")
        if "[]" in key:
            params[modified_key] = value
        else:
            params[key] = value if len(value) > 1 else value[0]

    for key, value in req.match_info.items():
        params[key] = value
    return params


def hash_content(content: str, strip_content=False) -> str:
    if strip_content:
        content = content.strip()
    return hashlib.md5(content.encode()).hexdigest()
