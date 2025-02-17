from sanic import Blueprint
from app.routes.chunks import chunks
from app.routes.auth_token import auth_token

blueprints = [chunks, auth_token]

binary_blueprints = Blueprint.group(*blueprints, url_prefix="v1")
