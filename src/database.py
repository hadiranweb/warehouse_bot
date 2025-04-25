import sqlite3

def init_db():
    conn = sqlite3.connect("warehouse.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity INTEGER NOT NULL
    )""")
    conn.commit()
    conn.close()

def add_item_to_db(name, quantity):
    conn = sqlite3.connect("warehouse.db")
    c = conn.cursor()
    c.execute("INSERT INTO items (name, quantity) VALUES (?, ?)", (name, quantity))
    conn.commit()
    conn.close()

def get_all_items():
    conn = sqlite3.connect("warehouse.db")
    c = conn.cursor()
    c.execute("SELECT id, name, quantity FROM items")
    items = c.fetchall()
    conn.close()
    return items

def delete_item_from_db(item_id):
    conn = sqlite3.connect("warehouse.db")
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE id = ?", (item_id,))
    row_count = c.rowcount
    conn.commit()
    conn.close()
    return row_count
