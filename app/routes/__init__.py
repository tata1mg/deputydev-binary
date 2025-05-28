from sanic import Blueprint

from app.routes.auth_token import auth_token
from app.routes.chunks import chunks
from app.routes.codebase_read import codebase_read
from app.routes.diff_applicator import diff_applicator
from app.routes.initialization import initialization
from app.routes.mcp import mcp
from app.routes.ping import ping
from app.routes.search import focus_search
from app.routes.shutdown import shutdown
from app.routes.url import url_reader

blueprints = [
    chunks,
    auth_token,
    diff_applicator,
    initialization,
    focus_search,
    shutdown,
    codebase_read,
    url_reader,
    mcp,
]

v1_binary_blueprints = Blueprint.group(*blueprints, url_prefix="v1")

binary_blueprints = Blueprint.group(v1_binary_blueprints, ping, url_prefix="")
