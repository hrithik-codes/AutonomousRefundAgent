import sqlite3
import random
import os
import time
from datetime import datetime, timedelta, timezone
from database import DB_PATH
import shopify_client

# -------------------------------------------------------------
# Curated Real-World E-Commerce Catalog & Customer Personas
# -------------------------------------------------------------
REALISTIC_PRODUCTS = [
    # Consumer Tech & Audio
    ("Apple AirPods Pro (2nd Gen) with MagSafe", 249.00, "Tech"),
    ("Sony WH-1000XM5 Wireless Noise-Cancelling Headphones", 348.00, "Tech"),
    ("Logitech MX Master 3S Wireless Mouse", 99.00, "Tech"),
    ("Anker MagGo 10,000mAh Magnetic Power Bank", 49.99, "Tech"),
    ("Kindle Paperwhite 16GB Display", 149.99, "Tech"),
    ("Belkin 3-in-1 Fast Wireless Charging Stand", 119.95, "Tech"),
    ("Bose SoundLink Flex Bluetooth Speaker", 129.00, "Tech"),
    ("Apple AirTag 4-Pack", 99.00, "Tech"),
    ("Samsung T7 Shield 1TB Portable SSD", 109.99, "Tech"),
    ("Keychron K2 Wireless Mechanical Keyboard", 79.99, "Tech"),
    ("Shure SM7B Vocal Microphone", 399.00, "Tech"),
    ("Razer DeathAdder V3 Pro Gaming Mouse", 149.99, "Tech"),

    # Apparel, Footwear & Outerwear
    ("Patagonia Better Sweater Fleece Jacket", 139.00, "Apparel"),
    ("Nike Air Max 270 Running Shoes", 160.00, "Footwear"),
    ("Lululemon Align High-Rise Pant 25\"", 98.00, "Apparel"),
    ("The North Face ThermoBall Eco Jacket 2.0", 220.00, "Apparel"),
    ("Birkenstock Boston Soft Footbed Suede Clogs", 160.00, "Footwear"),
    ("Levi's 501 Original Fit Men's Jeans", 79.50, "Apparel"),
    ("Arc'teryx Atom LT Insulated Hoody", 299.00, "Apparel"),
    ("On Cloud 5 Lightweight Running Shoes", 139.95, "Footwear"),
    ("Carhartt WIP Chase Sweatshirt", 88.00, "Apparel"),
    ("Allbirds Wool Runner Everyday Sneakers", 110.00, "Footwear"),
    ("Hoka Clifton 9 Road Running Shoes", 145.00, "Footwear"),

    # Home, Kitchen & Lifestyle
    ("Hydro Flask 32 oz Wide Mouth with Straw Lid", 44.95, "Lifestyle"),
    ("Yeti Tundra 45 Hard Cooler", 325.00, "Lifestyle"),
    ("Nespresso Vertuo Pop+ Deluxe Coffee Machine", 129.00, "Home"),
    ("Dyson Supersonic Hair Dryer", 429.00, "Home"),
    ("Le Creuset Enameled Cast Iron Dutch Oven 5.5 Qt", 385.00, "Home"),
    ("Aesop Resurrection Aromatique Hand Wash 500ml", 43.00, "Lifestyle"),
    ("Stanley Quencher H2.0 FlowState Tumbler 40 oz", 45.00, "Lifestyle"),
    ("Fellow Ode Gen 2 Brew Coffee Grinder", 345.00, "Home"),
    ("Philips Hue Smart Dimmer Starter Kit", 129.99, "Home"),
    ("Theragun Prime Percussive Massage Gun", 299.00, "Lifestyle"),
]

FIRST_NAMES = [
    "James", "Sophia", "Marcus", "Emma", "David", "Olivia", "Daniel", "Ava", "Michael", "Isabella",
    "Ethan", "Mia", "Alexander", "Charlotte", "Liam", "Amelia", "Noah", "Harper", "Benjamin", "Evelyn",
    "Lucas", "Abigail", "Henry", "Emily", "Sebastian", "Elizabeth", "Jack", "Avery", "Owen", "Ella"
]

LAST_NAMES = [
    "Miller", "Chen", "Johnson", "Davis", "Kim", "Taylor", "Martinez", "Wilson", "Brown", "Garcia",
    "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Robinson", "Clark", "Lewis"
]

CARRIERS = ["FedEx", "UPS", "USPS", "DHL Express"]
CHECKPOINTS = [
    "Austin, TX", "Denver, CO", "Louisville Hub, KY", "Memphis Sort Center, TN",
    "Inwood, NY", "Miami Sorting Facility, FL", "Seattle, WA", "Chicago Hub, IL",
    "Atlanta Distribution Center, GA", "Phoenix, AZ"
]

def generate_100_realistic_orders():
    print("🚀 Generating 100 realistic e-commerce orders & customer profiles...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear previous seed
    cursor.execute("DELETE FROM refund_audit_ledger")
    cursor.execute("DELETE FROM carrier_telemetry")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM customers")

    # Fixed seed for reproducibility
    random.seed(42)

    now = datetime.now(timezone.utc)

    for i in range(1, 101):
        order_num = f"ORD-{1000 + i}"
        cust_id = f"CUST-{100 + i}"
        
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{random.randint(10, 99)}@gmail.com"

        # Persona Distribution:
        # ~70% High-Trust VIPs (Fast zero-touch refunds)
        # ~20% Normal / Carrier Delayed (Weather/Exception)
        # ~10% High-Risk / Flagged Abuse (Circuit-breaker trips)
        tier_roll = random.random()

        if tier_roll < 0.70:
            # VIP / High Trust
            account_age = random.randint(180, 900)
            total_orders = random.randint(6, 35)
            past_disputes = 0
            trust_score = random.randint(80, 98)
            status = "Delivered"
            carrier_status = "Delivered"
            signed_by = None
            exception_reason = None
        elif tier_roll < 0.90:
            # Normal with occasional carrier delay
            account_age = random.randint(60, 300)
            total_orders = random.randint(2, 8)
            past_disputes = random.choice([0, 1])
            trust_score = random.randint(62, 79)
            status = "In Transit"
            carrier_status = "Exception / Delayed in Transit"
            signed_by = None
            exception_reason = "Severe Weather Delay at regional sort facility"
        else:
            # High-Risk / Fraud Profile
            account_age = random.randint(3, 40)
            total_orders = random.randint(1, 3)
            past_disputes = random.randint(2, 4)
            trust_score = random.randint(25, 48)
            status = "Delivered"
            carrier_status = "Delivered (Direct Signature Required)"
            signed_by = f"{first[0]}. {last}"
            exception_reason = None

        prod_name, prod_price, _ = random.choice(REALISTIC_PRODUCTS)
        # Add slight realistic price jitter (+/- $2)
        price = round(prod_price + random.uniform(-1.5, 1.5), 2)
        total_spend = round(price * total_orders * random.uniform(0.8, 1.2), 2)

        carrier_name = random.choice(CARRIERS)
        trk_num = f"{carrier_name[:3].upper()}-{random.randint(10000000, 99999999)}"
        checkpoint = random.choice(CHECKPOINTS)
        order_date = (now - timedelta(days=random.randint(2, 28))).strftime("%Y-%m-%d")

        # 1. Insert Customer
        cursor.execute("""
        INSERT INTO customers (id, name, email, account_age_days, total_orders, total_spend, past_disputes, trust_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (cust_id, name, email, account_age, total_orders, total_spend, past_disputes, trust_score))

        # 2. Insert Order
        cursor.execute("""
        INSERT INTO orders (order_number, customer_id, item_name, amount, order_date, status, carrier, tracking_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_num, cust_id, prod_name, price, order_date, status, carrier_name, trk_num))

        # 3. Insert Carrier Telemetry
        photo_url = f"https://cdn.carrier.mock/proof/{trk_num.lower()}.jpg" if status == "Delivered" else None
        cursor.execute("""
        INSERT INTO carrier_telemetry (tracking_number, carrier, status, last_checkpoint, delivered_at, signed_by, photo_proof_url, exception_reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (trk_num, carrier_name, carrier_status, checkpoint, order_date if status == "Delivered" else None, signed_by, photo_url, exception_reason))

    conn.commit()
    conn.close()
    print("✅ 100 realistic orders successfully populated into ecommerce.db!")

def sync_top_orders_to_shopify(count: int = 10):
    """Sync a batch of clean realistic orders to live Shopify so you can demo either."""
    print(f"\n🛍️ Syncing {count} realistic orders to live Shopify store ({shopify_client.SHOPIFY_STORE})...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders JOIN customers ON orders.customer_id = customers.id LIMIT ?", (count,))
    rows = cursor.fetchall()
    conn.close()

    created = 0
    for row in rows:
        try:
            res = shopify_client.create_sample_paid_order(
                item_name=row["item_name"],
                price=row["amount"],
                customer_name=row["name"],
                customer_email=row["email"]
            )
            if "order" in res:
                created += 1
                print(f"  • Created Shopify Order {res['order']['name']}: {row['item_name']} (${row['amount']:.2f}) for {row['name']}")
                # Brief sleep to avoid hitting Shopify leaky bucket limit
                time.sleep(0.5)
            else:
                print(f"  ⚠️ Error creating order: {res}")
        except Exception as e:
            print(f"  ⚠️ Exception syncing order: {e}")

    print(f"✅ Synced {created} orders to live Shopify store!")

if __name__ == "__main__":
    generate_100_realistic_orders()
    # Also sync 10 realistic orders to live Shopify for demo variety
    sync_top_orders_to_shopify(count=8)
    print("\n🎉 Complete! 100 orders in database + live Shopify synchronized.")
