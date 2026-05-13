"""
database/init_db.py  (UPDATED — thêm bảng accounts)
------------------------------------------------------
Đặt file này vào: database/init_db.py
Chạy: python database/init_db.py
"""

import hashlib
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "airline.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ── ACCOUNTS (MỚI THÊM) ────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            full_name     TEXT,
            role          TEXT    NOT NULL DEFAULT 'staff',
            created_at    TEXT    DEFAULT CURRENT_TIMESTAMP,
            last_login    TEXT
        )
    """)

    # ── FLIGHTS ────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            flight_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            airline_name    TEXT,
            departure       TEXT,
            destination     TEXT,
            departure_time  TEXT,
            arrival_time    TEXT,
            available_seats INTEGER,
            ticket_price    REAL
        )
    """)

    # ── PASSENGERS ─────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passengers (
            passenger_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name       TEXT,
            gender          TEXT,
            phone           TEXT,
            passport_number TEXT,
            email           TEXT
        )
    """)

    # ── BOOKINGS ───────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            passenger_id INTEGER,
            flight_id    INTEGER,
            seat_number  TEXT,
            booking_date TEXT,
            status       TEXT,
            FOREIGN KEY(passenger_id) REFERENCES passengers(passenger_id),
            FOREIGN KEY(flight_id)    REFERENCES flights(flight_id)
        )
    """)

    conn.commit()

    # ── Tạo tài khoản admin mặc định (nếu chưa có) ────────────────────────
    cursor.execute("SELECT COUNT(*) FROM accounts")
    count = cursor.fetchone()[0]
    if count == 0:
        default_hash = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("""
            INSERT INTO accounts (username, email, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        """, ("admin", "admin@jetjetair.com", default_hash, "Admin JetJet", "admin"))
        conn.commit()
        print("  → Tài khoản mặc định: admin / admin123")

    conn.close()
    print("✅ Database initialized successfully!")
    print("   Bảng: accounts, flights, passengers, bookings")


if __name__ == "__main__":
    init_db()