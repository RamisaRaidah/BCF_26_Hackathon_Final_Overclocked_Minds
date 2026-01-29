import os
import json
import time
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


ORDER_BASE_URL = os.getenv("ORDER_BASE_URL", "http://localhost:8000")
N_REQUESTS = int(os.getenv("N_REQUESTS", "100"))          
CONCURRENCY = int(os.getenv("CONCURRENCY", "20"))         
SKU = os.getenv("SKU", "PS5")
QTY = int(os.getenv("QTY", "1"))
USER_ID = int(os.getenv("USER_ID", "1"))
OUT_FILE = os.getenv("OUT_FILE", "server/load_test/results.jsonl")

CREATE_TIMEOUT = float(os.getenv("CREATE_TIMEOUT", "3"))
SHIP_TIMEOUT = float(os.getenv("SHIP_TIMEOUT", "3"))

_lock = threading.Lock()


def _write_jsonl(obj: dict):
    with _lock:
        with open(OUT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj) + "\n")


def create_order(session: requests.Session) -> dict:
    payload = {"user_id": USER_ID, "sku": SKU, "qty": QTY}
    t0 = time.perf_counter()
    r = session.post(f"{ORDER_BASE_URL}/orders", json=payload, timeout=CREATE_TIMEOUT)
    latency_ms = int((time.perf_counter() - t0) * 1000)

    try:
        data = r.json()
    except Exception:
        data = None

    if r.status_code != 201 or not data or "order" not in data or "id" not in data["order"]:
        return {
            "phase": "create",
            "ok": False,
            "http": r.status_code,
            "latency_ms": latency_ms,
            "error": "CREATE_FAILED",
            "body": data,
        }

    return {
        "phase": "create",
        "ok": True,
        "http": r.status_code,
        "latency_ms": latency_ms,
        "order_id": data["order"]["id"],
        "transaction_uuid": data["order"].get("transaction_uuid"),
    }


def ship_order(session: requests.Session, order_id: int) -> dict:
    t0 = time.perf_counter()
    r = session.post(f"{ORDER_BASE_URL}/orders/{order_id}/ship", timeout=SHIP_TIMEOUT)
    latency_ms = int((time.perf_counter() - t0) * 1000)

    try:
        data = r.json()
    except Exception:
        data = None

    result = "ERROR"
    if r.status_code == 200 and data and data.get("status") == "SHIPPED":
        result = "SHIPPED"
    elif r.status_code == 202 and data and data.get("status") == "SHIP_PENDING":
        result = "SHIP_PENDING"

    return {
        "phase": "ship",
        "order_id": order_id,
        "ok": result in ("SHIPPED", "SHIP_PENDING"),
        "http": r.status_code,
        "latency_ms": latency_ms,
        "result": result,
        "body": data,
    }


def worker(i: int) -> dict:
    with requests.Session() as session:
        # Create
        c = create_order(session)
        _write_jsonl({"i": i, **c})

        if not c.get("ok"):
            return {"i": i, "final": "CREATE_FAILED"}

        order_id = c["order_id"]

        # Ship
        s = ship_order(session, order_id)
        _write_jsonl({"i": i, **s})

        return {"i": i, "final": s["result"]}


def main():
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("")

    print(f"ORDER_BASE_URL={ORDER_BASE_URL}")
    print(f"N_REQUESTS={N_REQUESTS}  CONCURRENCY={CONCURRENCY}")
    print(f"Writing results to: {OUT_FILE}")

    t0 = time.time()
    summary = {"SHIPPED": 0, "SHIP_PENDING": 0, "ERROR": 0, "CREATE_FAILED": 0}

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futures = [ex.submit(worker, i) for i in range(1, N_REQUESTS + 1)]
        for fut in as_completed(futures):
            res = fut.result()
            final = res.get("final", "ERROR")
            summary[final] = summary.get(final, 0) + 1

    elapsed = round(time.time() - t0, 2)
    print(f"Done in {elapsed}s")
    print("Summary:", summary)
    print("Tip: open results.jsonl to show judges affected orders (SHIP_PENDING).")


if __name__ == "__main__":
    main()