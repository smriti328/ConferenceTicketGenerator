import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event_name TEXT,
    ticket_id TEXT,
    qr_code TEXT,
    pdf TEXT
)''')

conn.commit()
conn.close()