from sanic import Blueprint

from app.routes.auth_token import auth_token
from app.routes.diff_applicator import diff_applicator
from app.routes.chunks import chunks
from app.routes.initialization import initialization
from app.routes.ping import ping

blueprints = [chunks, auth_token, diff_applicator, initialization]

v1_binary_blueprints = Blueprint.group(*blueprints, url_prefix="v1")

binary_blueprints = Blueprint.group(v1_binary_blueprints, ping, url_prefix="")
