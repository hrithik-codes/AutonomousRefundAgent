from shopify_client import create_sample_paid_order, list_orders

print("Connecting to live Shopify store: fetchathon-ai.myshopify.com...")
print("Populating store with live test dispute orders...\n")

# Order 1: Alice Walker ($85.00 Headphones - VIP High Trust)
res1 = create_sample_paid_order(
    item_name="Wireless Noise-Cancelling Headphones Pro",
    price=85.00,
    customer_name="Alice Walker",
    customer_email="alice.walker@example.com"
)
if "order" in res1:
    print(f"✅ Created Order {res1['order']['name']} for Alice Walker ($85.00)")
else:
    print(f"Failed to create order 1: {res1}")

# Order 2: Bob Martinez ($75.00 Jacket - Carrier Delay)
res2 = create_sample_paid_order(
    item_name="Waterproof Trail Running Jacket",
    price=75.00,
    customer_name="Bob Martinez",
    customer_email="bob.martinez@example.com"
)
if "order" in res2:
    print(f"✅ Created Order {res2['order']['name']} for Bob Martinez ($75.00)")
else:
    print(f"Failed to create order 2: {res2}")

# Order 3: Charlie Vance ($280.00 Watch - Fraud Risk)
res3 = create_sample_paid_order(
    item_name="Designer Smart Watch Titanium Edition",
    price=280.00,
    customer_name="Charlie Vance",
    customer_email="charlie.v@example.com"
)
if "order" in res3:
    print(f"✅ Created Order {res3['order']['name']} for Charlie Vance ($280.00)")
else:
    print(f"Failed to create order 3: {res3}")

print("\n--- Current Live Orders in Shopify Store ---")
for o in list_orders(limit=10):
    cust = o.get("customer") or {}
    print(f"• Order {o.get('name')}: {o.get('total_price')} USD | Customer: {cust.get('first_name')} {cust.get('last_name')} ({o.get('financial_status')})")
