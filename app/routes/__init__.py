from sanic import Blueprint

from app.routes.auth_token import auth_token
from app.routes.diff_applicator import diff_applicator
from app.routes.chunks import chunks

blueprints = [chunks, auth_token, diff_applicator]

binary_blueprints = Blueprint.group(*blueprints, url_prefix="v1")
