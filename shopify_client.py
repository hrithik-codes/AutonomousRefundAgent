import os
import certifi
import json
import urllib.request
import urllib.error

# Fix macOS SSL
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# Load local .env if present
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k] = v

SHOPIFY_STORE = os.environ.get("SHOPIFY_STORE", "fetchathon-ai.myshopify.com").strip()
SHOPIFY_API_VERSION = "2024-01"
SHOPIFY_TOKEN = os.environ.get("SHOPIFY_TOKEN", "").strip()

BASE_URL = f"https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}"

def _shopify_request(endpoint: str, method: str = "GET", payload: dict = None):
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8") if payload else None
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "X-Shopify-Access-Token": SHOPIFY_TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method=method,
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"Shopify API HTTP Error ({e.code}): {error_body}")
        return {"error": e.code, "message": error_body}
    except Exception as e:
        print(f"Shopify Connection Error: {e}")
        return {"error": 500, "message": str(e)}

def list_orders(limit: int = 10):
    """Retrieve recent orders from Shopify store."""
    res = _shopify_request(f"/orders.json?status=any&limit={limit}")
    return res.get("orders", [])

def get_order_by_name(order_name: str):
    """Find a Shopify order by its display name (e.g. '#1001' or '1001')."""
    clean_name = order_name.strip()
    if not clean_name.startswith("#"):
        clean_name = f"#{clean_name}"
        
    orders = list_orders(limit=50)
    for o in orders:
        if o.get("name") == clean_name or str(o.get("order_number")) == order_name.replace("#", ""):
            return o
    return None

def issue_shopify_refund(order_id: int, amount: float, note: str = "Autonomous Agent Resolution"):
    """Trigger a refund directly on a Shopify order."""
    # 1. Fetch order to get transaction details
    order_data = _shopify_request(f"/orders/{order_id}.json")
    order = order_data.get("order")
    if not order:
        return {"success": False, "message": "Order not found on Shopify"}

    # 2. Find parent transaction
    tx_data = _shopify_request(f"/orders/{order_id}/transactions.json")
    transactions = tx_data.get("transactions", [])
    parent_tx = next((t for t in transactions if t.get("status") == "success" and t.get("kind") in ["sale", "capture"]), None)

    refund_payload = {
        "refund": {
            "currency": order.get("currency", "USD"),
            "notify": True,
            "note": note,
            "transactions": []
        }
    }

    if parent_tx:
        refund_payload["refund"]["transactions"].append({
            "parent_id": parent_tx["id"],
            "amount": str(amount),
            "kind": "refund",
            "gateway": parent_tx.get("gateway", "manual")
        })

    res = _shopify_request(f"/orders/{order_id}/refunds.json", method="POST", payload=refund_payload)
    if "refund" in res:
        return {"success": True, "refund": res["refund"]}
    else:
        return {"success": False, "error": res}

def create_sample_paid_order(item_name: str, price: float, customer_name: str, customer_email: str):
    """Create a realistic completed order directly on Shopify for testing."""
    first, *last = customer_name.split()
    last_name = " ".join(last) if last else "Customer"

    payload = {
        "order": {
            "email": customer_email,
            "fulfillment_status": "fulfilled",
            "financial_status": "paid",
            "send_receipt": False,
            "line_items": [
                {
                    "title": item_name,
                    "price": f"{price:.2f}",
                    "quantity": 1
                }
            ],
            "customer": {
                "first_name": first,
                "last_name": last_name,
                "email": customer_email
            },
            "transactions": [
                {
                    "kind": "sale",
                    "status": "success",
                    "amount": f"{price:.2f}"
                }
            ]
        }
    }
    return _shopify_request("/orders.json", method="POST", payload=payload)

if __name__ == "__main__":
    print("Testing Shopify Client...")
    print("Store:", SHOPIFY_STORE)
