from sanic import Sanic
from app.routes import binary_blueprints
import sys

app = Sanic("WebSocketServer")
app.blueprint(binary_blueprints)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000  # Default: 8000
    app.run(host="0.0.0.0", port=port, debug=False, legacy=True)
