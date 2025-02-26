from sanic import Blueprint

from app.routes.auth_token import auth_token
from app.routes.chunks import chunks

blueprints = [chunks, auth_token]

binary_blueprints = Blueprint.group(*blueprints, url_prefix="v1")
