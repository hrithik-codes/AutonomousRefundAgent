import sqlite3
import os
from database import DB_PATH, init_db
import shopify_client

def reset_local_database():
    """Wipes the audit ledger and resets the local SQLite database."""
    print("🧹 Resetting local database (ecommerce.db)...")
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM refund_audit_ledger")
        cursor.execute("UPDATE orders SET status = 'Delivered' WHERE order_number = 'ORD-9011'")
        cursor.execute("UPDATE orders SET status = 'In Transit' WHERE order_number = 'ORD-8042'")
        cursor.execute("UPDATE orders SET status = 'Delivered' WHERE order_number = 'ORD-7033'")
        conn.commit()
        conn.close()
    else:
        init_db()
    print("✅ Local database reset! Audit ledger is clean.\n")

def reset_shopify_orders():
    """Creates a fresh batch of clean, un-refunded 'Paid' orders on Shopify."""
    print("🛍️ Connecting to Shopify store: fetchathon-ai.myshopify.com...")
    
    # Create fresh Paid orders ready for demo
    # 1. Fresh Alice Walker ($85 Headphones - High Trust, Un-refunded)
    res1 = shopify_client.create_sample_paid_order(
        item_name="Wireless Noise-Cancelling Headphones Pro",
        price=85.00,
        customer_name="Alice Walker",
        customer_email="alice.walker@example.com"
    )
    name1 = res1.get("order", {}).get("name", "New")

    # 2. Fresh Bob Martinez ($75 Jacket - Carrier Delay, Un-refunded)
    res2 = shopify_client.create_sample_paid_order(
        item_name="Waterproof Trail Running Jacket",
        price=75.00,
        customer_name="Bob Martinez",
        customer_email="bob.martinez@example.com"
    )
    name2 = res2.get("order", {}).get("name", "New")

    # 3. Fresh Charlie Vance ($280 Watch - Fraud Risk, Un-refunded)
    res3 = shopify_client.create_sample_paid_order(
        item_name="Designer Smart Watch Titanium Edition",
        price=280.00,
        customer_name="Charlie Vance",
        customer_email="charlie.v@example.com"
    )
    name3 = res3.get("order", {}).get("name", "New")

    print(f"✅ Created fresh order {name1} for Alice Walker ($85.00 - Status: Paid)")
    print(f"✅ Created fresh order {name2} for Bob Martinez ($75.00 - Status: Paid)")
    print(f"✅ Created fresh order {name3} for Charlie Vance ($280.00 - Status: Paid)")

    print("\n--- Current Fresh Shopify Orders (Ready for Live Demo) ---")
    orders = shopify_client.list_orders(limit=6)
    for o in orders:
        cust = o.get("customer") or {}
        print(f"• {o.get('name')}: {o.get('total_price')} USD | {cust.get('first_name')} {cust.get('last_name')} | Status: {o.get('financial_status').upper()}")

if __name__ == "__main__":
    reset_local_database()
    reset_shopify_orders()
    print("\n🎉 All orders reset and ready for your live video recording!")
