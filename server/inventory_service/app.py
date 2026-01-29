from flask import Flask, jsonify, request
from datetime import timedelta
import time
import logging
import os
import uuid
from db import get_db_connection, execute_query

app = Flask(__name__)

logging.basicConfig (
    filename = "app.log",
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s"
)

@app.route("/")
def home():
    return "Biday prithibi"

# modeling gremlin
GREMLIN_EVERY_N = int(os.environ["GREMLIN_EVERY_N"])            
GREMLIN_DELAY_SECONDS = float(os.environ["GREMLIN_DELAY_SECONDS"])
CRASH_EVERY_N = int(os.environ["CRASH_EVERY_N"])               
CALL_COUNT = 0

def gremlin_delay():
    global CALL_COUNT
    CALL_COUNT += 1
    if GREMLIN_EVERY_N > 0 and (CALL_COUNT % GREMLIN_EVERY_N == 0):
        time.sleep(GREMLIN_DELAY_SECONDS)

def crash_after_commit():
    if CRASH_EVERY_N > 0 and (CALL_COUNT % CRASH_EVERY_N == 0):
        os._exit(1)  

# API endpoints
@app.route("/health")
def health(): 
    row = execute_query("SELECT 1 AS ok FROM stock LIMIT 1;", fetch_one = True)
    if row is None:
        return jsonify({"status": "error", "detail": "db unreachable or schema missing"}), 500
    return jsonify({"status": "ok"}), 200 

@app.get("/inventory/adjust/<txn>")
def get_adjustment(txn):
    try:
        txn_uuid = str(uuid.UUID(txn))
    except Exception:
        return jsonify({"status": "error", "detail": "invalid transaction_uuid"}), 400
    row = execute_query(
        "SELECT transaction_uuid, sku, qty, applied_at FROM adjustments WHERE transaction_uuid = %s;",
        (txn_uuid,),
        fetch_one = True,
    )
    if not row:
        return jsonify({"status": "NOT FOUND"}), 404
    return jsonify({"status": "APPLIED", "data": row}), 200

@app.post("/inventory/adjust")
def adjust_inventory():
    gremlin_delay()

    data = request.get_json(silent = True) or {}
    transaction_uuid = data.get("transaction_uuid")
    sku = data.get("sku")
    qty = data.get("qty")

    if not transaction_uuid or not sku or qty is None:
        return jsonify({"status": "error", "detail": "required: transaction_uuid, sku, qty"}), 400

    try:
        txn_uuid = str(uuid.UUID(str(transaction_uuid)))
    except Exception:
        return jsonify({"status": "error", "detail": "invalid transaction_uuid"}), 400

    try:
        qty = int(qty)
        if qty <= 0:
            raise ValueError()
    except Exception:
        return jsonify({"status": "error", "detail": "qty must be int > 0"}), 400

    sku = str(sku).strip().upper()

    connection = get_db_connection()
    if connection is None:
        return jsonify({"status": "error", "detail": "db connection failed"}), 500
    try:
        with connection:  
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM adjustments WHERE transaction_uuid = %s;",
                    (txn_uuid,),
                )
                if cursor.fetchone() is not None:
                    return jsonify({"status": "ALREADY_APPLIED"}), 200

                cursor.execute(
                    "SELECT available FROM stock WHERE sku = %s FOR UPDATE;",
                    (sku,),
                )
                row = cursor.fetchone()
                if row is None:
                    return jsonify({"status": "error", "detail": "SKU not found"}), 404

                available = int(row[0])
                if available < qty:
                    return jsonify({"status": "error", "detail": "INSUFFICIENT_STOCK", "available": available}), 409

                cursor.execute(
                    "UPDATE stock SET available = available - %s WHERE sku = %s;",
                    (qty, sku),
                )

                cursor.execute(
                    "INSERT INTO adjustments(transaction_uuid, sku, qty) VALUES (%s, %s, %s);",
                    (txn_uuid, sku, qty),
                )

        crash_after_commit()

        return jsonify({"status": "APPLIED"}), 200

    except Exception as e:
        logging.error(f"/inventory/adjust failed: {e}")
        try:
            connection.rollback()
        except Exception:
            pass
        return jsonify({"status": "error", "detail": "internal error"}), 500

    finally:
        try:
            connection.close()
        except Exception:
            pass

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = os.environ["INVENTORY_PORT"], debug = True)