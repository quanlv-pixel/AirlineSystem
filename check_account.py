import sqlite3

conn = sqlite3.connect("database/airline.db")
cur = conn.cursor()

cur.execute("""
    SELECT account_id, username, email, role
    FROM accounts
""")

rows = cur.fetchall()

for row in rows:
    print(row)

conn.close()