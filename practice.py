import sqlite3

conn=sqlite3.connect("practice.db")
cursor=conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity REAL NOT NULL
    )
""")

conn.commit()

cursor.execute("""
    CREATE TABLE test_no_commit (
        id INTEGER PRIMARY KEY
    )
""")

cursor.execute(
    "INSERT INTO inventory (name, quantity) VALUES (?, ?)",
    ("Chicken", 50)
)
conn.commit()

conn.close()