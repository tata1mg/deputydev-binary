from sanic import Sanic
from app.routes import binary_blueprints

app = Sanic("WebSocketServer")
app.blueprint(binary_blueprints)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True, legacy=True)
