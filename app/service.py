import multiprocessing
import os
import sys

import certifi
from sanic import Sanic

from app.listeners import listeners
from app.routes import binary_blueprints

try:
    if sys.platform == "win32":
        multiprocessing.set_start_method("spawn", force=True)
    else:
        multiprocessing.set_start_method("fork", force=True)
except RuntimeError:
    pass
app = Sanic("BinaryServer")
app.blueprint(binary_blueprints)
app.config.REQUEST_TIMEOUT = 3000
app.config.RESPONSE_TIMEOUT = 3000
app.config.KEEP_ALIVE_TIMEOUT = 3000
app.config.TOUCHUP = False
app.config.WEBSOCKET_MAX_SIZE = 10 * 1024 * 1024  # 10 MB

for listener in listeners:
    app.register_listener(listener[0], listener[1])


def main() -> None:
    multiprocessing.freeze_support()
    os.environ["SSL_CERT_FILE"] = f"{certifi.where()}"
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"  # Default: localhost
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8001  # Default: 8001
    app.run(host=host, port=port, debug=False, legacy=True)


if __name__ == "__main__":
    main()
