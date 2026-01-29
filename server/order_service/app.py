from flask import Flask, jsonify, render_template, request
import logging
import os
import time
from db import get_db_connection, execute_query
import uuid
from inventory_client import adjust_inventory, check_adjustment
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
    status = latency_tracker.status()
    if status == "red":
        return render_template("red.html")
    else:
        return render_template("green.html")
    # return jsonify({
    #     "avg_30s_ms": round(latency_tracker.avg_ms(), 2),
    #     "status": latency_tracker.status()
    # }), 200

@app.route("/orders", methods = ["POST"])
def create_order():
    data = request.get_json(silent = True) or {}
    user_id = data.get("user_id")
    sku = data.get("sku")
    qty = data.get("qty", 1)
    if user_id is None or not sku:
        return jsonify({"status": "error", "detail": "required: user_id, sku"}), 400
    try:
        user_id = int(user_id)
        qty = int(qty)
        if qty <= 0:
            raise ValueError()
    except Exception:
        return jsonify({"status": "error", "detail": "user_id must be int, qty must be int > 0"}), 400
    sku = str(sku).strip().upper()
    txn_uuid = str(uuid.uuid4())
    row = execute_query(
        """
            INSERT INTO orders (transaction_uuid, user_id, sku, quantity, order_status, updated_at)
            VALUES (%s, %s, %s, %s, 'PENDING', CURRENT_TIMESTAMP)
            RETURNING id, transaction_uuid, user_id, sku, quantity, order_status, created_at, updated_at;
        """,
        (txn_uuid, user_id, sku, qty),
        fetch_one=True,
    )
    if not row:
        return jsonify({"status": "error", "detail": "failed to create order"}), 500
    return jsonify({"status": "created", "order": row}), 201

def _set_order_status(order_id: int, status: str):
    execute_query(
        "UPDATE orders SET order_status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s;",
        (status, order_id),
    )

@app.route("/orders/<int:order_id>/ship", methods = ["POST"])
def ship_order(order_id: int):
    order = execute_query(
        "SELECT id, transaction_uuid, sku, quantity, order_status FROM orders WHERE id = %s;",
        (order_id,),
        fetch_one=True,
    )
    if not order:
        return jsonify({"status": "error", "detail": "order not found"}), 404
 
    txn_uuid = order["transaction_uuid"]
    sku = order["sku"]
    qty = int(order["quantity"])
 
    ok, http_status, data, err, elapsed_ms = adjust_inventory(txn_uuid, sku, qty)
 
    _log_inventory_call(order_id, txn_uuid, http_status, elapsed_ms, err or _err_from_resp(http_status, data))
 
    if http_status == 200 and data and data.get("status") in ("APPLIED", "ALREADY_APPLIED"):
        _set_order_status(order_id, "SHIPPED")
        return jsonify({"status": "SHIPPED", "transaction_uuid": txn_uuid}), 200
 
    if http_status == 409:
        _set_order_status(order_id, "PENDING")
        return jsonify({"status": "error", "detail": "INSUFFICIENT_STOCK"}), 409
 
    if http_status == 404:
        _set_order_status(order_id, "PENDING")
        return jsonify({"status": "error", "detail": "SKU_NOT_FOUND"}), 404
 
    applied, _, _ = check_adjustment(txn_uuid)
    if applied:
        _set_order_status(order_id, "SHIPPED")
        return jsonify({"status": "SHIPPED", "note": "confirmed after uncertainty", "transaction_uuid": txn_uuid}), 200
 
    _set_order_status(order_id, "SHIP_PENDING")
    return jsonify({
        "status": "SHIP_PENDING",
        "message": "Inventory is slow/unreachable. Please retry shipping later.",
        "transaction_uuid": txn_uuid
    }), 202

def _log_inventory_call(order_id: int, txn_uuid: str, http_status: int | None, elapsed_ms: int | None, error_message: str | None):
    execute_query(
        """
            INSERT INTO inventory_calls (order_id, transaction_uuid, http_status_code, response_time_ms, error_message)
            VALUES (%s, %s, %s, %s, %s);
        """,
        (order_id, txn_uuid, http_status, elapsed_ms, error_message),
    )

def _err_from_resp(http_status, data):
    if http_status is None:
        return "NO_RESPONSE"
    if http_status >= 500:
        return "INVENTORY_5XX"
    if not data:
        return f"HTTP_{http_status}"
    if isinstance(data, dict) and data.get("detail"):
        return str(data.get("detail"))
    return f"HTTP_{http_status}"

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = os.environ["ORDER_PORT"], debug = True)