from sanic import Blueprint
from app.routes.websockets import websocket_routes
from app.routes.https import http_routes

blueprints = [websocket_routes, http_routes]

binary_blueprints = Blueprint.group(*blueprints, url_prefix="v1")
