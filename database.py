import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "ecommerce.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Customers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        account_age_days INTEGER NOT NULL,
        total_orders INTEGER NOT NULL,
        total_spend REAL NOT NULL,
        past_disputes INTEGER NOT NULL,
        trust_score INTEGER NOT NULL
    )
    """)

    # 2. Orders Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_number TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        item_name TEXT NOT NULL,
        amount REAL NOT NULL,
        order_date TEXT NOT NULL,
        status TEXT NOT NULL,
        carrier TEXT NOT NULL,
        tracking_number TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
    """)

    # 3. Carrier Telemetry Table (Mock FedEx/UPS/USPS live carrier data)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS carrier_telemetry (
        tracking_number TEXT PRIMARY KEY,
        carrier TEXT NOT NULL,
        status TEXT NOT NULL,
        last_checkpoint TEXT NOT NULL,
        delivered_at TEXT,
        signed_by TEXT,
        photo_proof_url TEXT,
        exception_reason TEXT
    )
    """)

    # 4. Refund & Escalation Audit Ledger
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS refund_audit_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT NOT NULL,
        amount REAL NOT NULL,
        decision TEXT NOT NULL,
        reason TEXT NOT NULL,
        transaction_id TEXT,
        escalation_brief TEXT,
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()
    seed_data(conn)
    conn.close()

def seed_data(conn):
    cursor = conn.cursor()
    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] > 0:
        return

    # Seed 3 Distinct Test Personas:
    # 1. Alice: VIP High Trust (Instant Auto-Refund & Label)
    cursor.execute("""
    INSERT INTO customers VALUES 
    ('CUST-001', 'Alice Walker', 'alice.walker@example.com', 450, 16, 2450.00, 0, 95)
    """)
    cursor.execute("""
    INSERT INTO orders VALUES 
    ('ORD-9011', 'CUST-001', 'Wireless Noise-Cancelling Headphones Pro', 85.00, '2026-10-18', 'Delivered', 'FedEx', 'FDX-9011-TRK')
    """)
    cursor.execute("""
    INSERT INTO carrier_telemetry VALUES 
    ('FDX-9011-TRK', 'FedEx', 'Delivered', 'Front Porch, Austin TX', '2026-10-20 14:15:00', NULL, 'https://cdn.carrier.mock/proof/fdx9011.jpg', NULL)
    """)

    # 2. Bob: Average Buyer with Carrier Delay (Carrier Telemetry Proof)
    cursor.execute("""
    INSERT INTO customers VALUES 
    ('CUST-002', 'Bob Martinez', 'bob.martinez@example.com', 180, 5, 420.00, 0, 78)
    """)
    cursor.execute("""
    INSERT INTO orders VALUES 
    ('ORD-8042', 'CUST-002', 'Waterproof Trail Running Jacket', 75.00, '2026-10-14', 'In Transit', 'UPS', 'UPS-8042-TRK')
    """)
    cursor.execute("""
    INSERT INTO carrier_telemetry VALUES 
    ('UPS-8042-TRK', 'UPS', 'Exception / Delayed', 'Distribution Center, Denver CO', NULL, NULL, NULL, 'Severe Weather Halt - Delayed past ETA by 4 days')
    """)

    # 3. Charlie: Flagged Abuser / High-Value Fraud Risk (Circuit Breakers Triggered)
    cursor.execute("""
    INSERT INTO customers VALUES 
    ('CUST-003', 'Charlie Vance', 'charlie.v@example.com', 9, 1, 280.00, 2, 32)
    """)
    cursor.execute("""
    INSERT INTO orders VALUES 
    ('ORD-7033', 'CUST-003', 'Designer Smart Watch Titanium Edition', 280.00, '2026-10-16', 'Delivered', 'USPS', 'USPS-7033-TRK')
    """)
    cursor.execute("""
    INSERT INTO carrier_telemetry VALUES 
    ('USPS-7033-TRK', 'USPS', 'Delivered', 'Recipient Front Desk, Miami FL', '2026-10-19 11:30:00', 'C. Vance', 'https://cdn.carrier.mock/proof/usps7033.jpg', NULL)
    """)

    conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized and seeded successfully with 3 test scenarios!")
