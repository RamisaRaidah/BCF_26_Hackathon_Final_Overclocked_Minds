# server/inventory-service/app.py
import os
import time
import uuid
import logging

from flask import Flask, request, jsonify

from db import get_db_connection, execute_query

app = Flask(__name__)

# ---------- Gremlin knobs ----------
GREMLIN_EVERY_N = int(os.getenv("GREMLIN_EVERY_N", "5"))            # every Nth request slow
GREMLIN_DELAY_SECONDS = float(os.getenv("GREMLIN_DELAY_SECONDS", "3"))
CRASH_EVERY_N = int(os.getenv("CRASH_EVERY_N", "0"))               # 0 = disabled

CALL_COUNT = 0


def maybe_gremlin_delay():
    global CALL_COUNT
    CALL_COUNT += 1
    if GREMLIN_EVERY_N > 0 and (CALL_COUNT % GREMLIN_EVERY_N == 0):
        time.sleep(GREMLIN_DELAY_SECONDS)


def maybe_crash_after_commit():
    """
    Simulates: commit succeeded but response never returned.
    Enable with CRASH_EVERY_N > 0.
    """
    if CRASH_EVERY_N > 0 and (CALL_COUNT % CRASH_EVERY_N == 0):
        os._exit(1)  # hard crash


# ---------- Endpoints ----------
# @app.get("/health")
# def health():
#     row = execute_query("SELECT 1 AS ok FROM stock LIMIT 1;", fetch_one=True)
#     if row is None:
#         return jsonify({"status": "error", "detail": "db unreachable or schema missing"}), 500
#     return jsonify({"status": "ok"}), 200


@app.get("/inventory/adjust/<txn>")
def get_adjustment(txn):
    try:
        txn_uuid = str(uuid.UUID(txn))
    except Exception:
        return jsonify({"status": "error", "detail": "invalid transaction_uuid"}), 400

    row = execute_query(
        "SELECT transaction_uuid, sku, qty, applied_at FROM adjustments WHERE transaction_uuid = %s;",
        (txn_uuid,),
        fetch_one=True,
    )
    if not row:
        return jsonify({"status": "NOT_FOUND"}), 404

    return jsonify({"status": "APPLIED", "data": row}), 200


@app.post("/inventory/adjust")
def adjust_inventory():
    maybe_gremlin_delay()

    data = request.get_json(silent=True) or {}
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

    # --- atomic transaction: idempotency + stock decrement ---
    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "detail": "db connection failed"}), 500

    try:
        with conn:  # commits on success, rollbacks on exception
            with conn.cursor() as cur:
                # 1) idempotency check
                cur.execute(
                    "SELECT 1 FROM adjustments WHERE transaction_uuid = %s;",
                    (txn_uuid,),
                )
                if cur.fetchone() is not None:
                    return jsonify({"status": "ALREADY_APPLIED"}), 200

                # 2) lock the row (prevents race under load)
                cur.execute(
                    "SELECT available FROM stock WHERE sku = %s FOR UPDATE;",
                    (sku,),
                )
                row = cur.fetchone()
                if row is None:
                    return jsonify({"status": "error", "detail": "SKU not found"}), 404

                available = int(row[0])
                if available < qty:
                    return jsonify({"status": "error", "detail": "INSUFFICIENT_STOCK", "available": available}), 409

                # 3) decrement stock
                cur.execute(
                    "UPDATE stock SET available = available - %s WHERE sku = %s;",
                    (qty, sku),
                )

                # 4) record adjustment (idempotency ledger)
                cur.execute(
                    "INSERT INTO adjustments(transaction_uuid, sku, qty) VALUES (%s, %s, %s);",
                    (txn_uuid, sku, qty),
                )

        # commit happened here
        maybe_crash_after_commit()

        return jsonify({"status": "APPLIED"}), 200

    except Exception as e:
        logging.error(f"/inventory/adjust failed: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return jsonify({"status": "error", "detail": "internal error"}), 500

    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    # For local runs without docker
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")), debug=True)
