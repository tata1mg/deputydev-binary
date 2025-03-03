import sys

from sanic import Sanic

from app.listeners import listeners
from app.routes import binary_blueprints

app = Sanic("BinaryServer")
app.blueprint(binary_blueprints)

for listener in listeners:
    app.register_listener(listener[0], listener[1])


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000  # Default: 8000
    app.run(host="0.0.0.0", port=port, debug=False, legacy=True)
