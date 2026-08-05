import sqlite3
from datetime import date, timedelta
import random


DB_PATH = "food_manager.db"

def get_connection():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
    item_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL UNIQUE,
    quantity      REAL NOT NULL,
    unit          TEXT NOT NULL,
    expiry_date   TEXT,
    reorder_threshold REAL DEFAULT 0)
    
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_history(
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id       INTEGER NOT NULL,
    date          TEXT NOT NULL,
    quantity_sold REAL NOT NULL,
    FOREIGN KEY (item_id) REFERENCES inventory(item_id))
    """)
    
    conn.commit()
    conn.close()

def seed_sample_data():
    conn = get_connection()
    cursor = conn.cursor()

    items = [
        ("Chicken", 50, "kg", "2026-08-10", 10),
        ("Rice", 100, "kg", None, 20),
        ("Tomatoes", 30, "kg", "2026-08-05", 5),
        ("Milk", 40, "liters", "2026-08-03", 10),
    ]

    today = date.today()
    for item in items:
        cursor.execute(
            "INSERT INTO inventory (name, quantity, unit, expiry_date, reorder_threshold) VALUES (?, ?, ?, ?, ?)",
            item
        )
        item_id = cursor.lastrowid
        for i in range(14):
            d = today - timedelta(days=i)
            is_weekend = d.weekday() >= 5
            if is_weekend:
                quantity=random.randint(30, 60)
            else:
                quantity=random.randint(10,30)
            cursor.execute(
            "INSERT INTO sales_history (item_id, date, quantity_sold) VALUES (?, ?, ?)",
            (item_id, str(d), quantity)
            )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_sample_data()
    print("Database seeded.")