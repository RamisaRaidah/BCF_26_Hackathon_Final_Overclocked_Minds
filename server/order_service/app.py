from flask import Flask, jsonify, request
import logging
import os
import time
from db import get_db_connection, execute_query
# from inventory_client import adjust_inventory, check_adjustment
from metrics import RollingLatency

app = Flask(__name__)

logging.basicConfig (
    filename = "app.log",
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s"
)

latency_tracker = RollingLatency()

def _now_ms():
    return int(time.time() * 1000)

@app.before_request
def mark_start():
    request._start_ms = _now_ms()

@app.after_request
def track_latency(response):
    try:
        start = getattr(request, "_start_ms", None)
        if start is not None:
            latency_tracker.add(_now_ms() - start)
    except Exception:
        pass
    return response

# API endpoints
@app.route("/")
def home():
    return "Order"

@app.route("/health")
def health():
    row = execute_query("SELECT 1 AS ok FROM orders LIMIT 1;", fetch_one = True)
    if row is None:
        return jsonify({"status": "error", "detail": "order_db unreachable or schema missing"}), 500
    return jsonify({"status": "ok"}), 200

@app.route("/metrics")
def metrics():
    return jsonify({
        "avg_30s_ms": round(latency_tracker.avg_ms(), 2),
        "status": latency_tracker.status()
    }), 200



# @app.route("/alert")
# def alert():
    

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = os.environ["ORDER_PORT"], debug = True)