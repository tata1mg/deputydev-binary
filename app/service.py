import multiprocessing
import sys

from sanic import Sanic
from app.listeners import listeners
from app.routes import binary_blueprints

app = Sanic("BinaryServer")
app.blueprint(binary_blueprints)
app.config.REQUEST_TIMEOUT = 3000
app.config.RESPONSE_TIMEOUT = 3000
app.config.KEEP_ALIVE_TIMEOUT = 3000
app.config.TOUCHUP = False
app.config.WEBSOCKET_MAX_SIZE = 10 * 1024 * 1024  # 10 MB

for listener in listeners:
    app.register_listener(listener[0], listener[1])

if __name__ == "__main__":
    multiprocessing.freeze_support()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001  # Default: 8001
    app.run(host="0.0.0.0", port=port, debug=False, legacy=True)
