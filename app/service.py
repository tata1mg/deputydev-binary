from sanic import Sanic

from app.routes import binary_blueprints

app = Sanic("WebSocketServer")
app.blueprint(binary_blueprints)
app.config.REQUEST_TIMEOUT = 300
app.config.RESPONSE_TIMEOUT = 300
app.config.KEEP_ALIVE_TIMEOUT = 300

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=False, legacy=True)
