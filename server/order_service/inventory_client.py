import os
import requests
 
INVENTORY_BASE_URL = os.getenv("INVENTORY_BASE_URL", "http://inventory_service:8001")
INVENTORY_TIMEOUT_SECONDS = float(os.getenv("INVENTORY_TIMEOUT_SECONDS", "1.0"))
INVENTORY_CHECK_TIMEOUT_SECONDS = float(os.getenv("INVENTORY_CHECK_TIMEOUT_SECONDS", "0.6"))
 
def adjust_inventory(transaction_uuid: str, sku: str, qty: int):
    """
    Returns: (ok: bool, http_status: int|None, data: dict|None, error: str|None, elapsed_ms: int|None)
    """
    url = f"{INVENTORY_BASE_URL}/inventory/adjust"
    payload = {"transaction_uuid": transaction_uuid, "sku": sku, "qty": qty}
 
    try:
        r = requests.post(url, json=payload, timeout=INVENTORY_TIMEOUT_SECONDS)
        elapsed_ms = int(r.elapsed.total_seconds() * 1000)
        data = None
        try:
            data = r.json()
        except Exception:
            data = None
        return (r.status_code < 500 and r.status_code != 0, r.status_code, data, None, elapsed_ms)
    except requests.Timeout:
        return (False, None, None, "TIMEOUT", None)
    except requests.RequestException as e:
        return (False, None, None, f"REQUEST_ERROR: {e}", None)
 
def check_adjustment(transaction_uuid: str):
    """
    Returns: (applied: bool, http_status: int|None, data: dict|None)
    """
    url = f"{INVENTORY_BASE_URL}/inventory/adjust/{transaction_uuid}"
    try:
        r = requests.get(url, timeout=INVENTORY_CHECK_TIMEOUT_SECONDS)
        data = None
        try:
            data = r.json()
        except Exception:
            data = None
        if r.status_code == 200 and data and data.get("status") == "APPLIED":
            return (True, r.status_code, data)
        return (False, r.status_code, data)
    except Exception:
        return (False, None, None)