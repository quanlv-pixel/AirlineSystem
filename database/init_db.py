"""
database/init_db.py
------------------------------------------------------
Khởi tạo toàn bộ database cho:
- Management App
- Booking App

Chạy:
python database/init_db.py
"""

import sqlite3
import hashlib
import os

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "airline.db"
)


def get_connection():

    conn = sqlite3.connect(DB_PATH)

    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def init_db():

    conn = get_connection()

    cursor = conn.cursor()

    # =========================================================
    # ACCOUNTS
    # =========================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (

            account_id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT NOT NULL UNIQUE,

            email TEXT NOT NULL UNIQUE,

            password_hash TEXT NOT NULL,

            full_name TEXT,

            role TEXT NOT NULL DEFAULT 'staff',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            last_login TEXT
        )
    """)

    # =========================================================
    # FLIGHTS
    # =========================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (

            flight_id INTEGER PRIMARY KEY AUTOINCREMENT,

            flight_number TEXT NOT NULL UNIQUE,

            airline_name TEXT,

            aircraft TEXT,

            departure TEXT,

            destination TEXT,

            departure_time TEXT,

            arrival_time TEXT,

            duration TEXT,

            gate TEXT,

            terminal TEXT,

            status TEXT DEFAULT 'Scheduled',

            total_seats INTEGER,

            available_seats INTEGER,

            ticket_price REAL,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # =========================================================
    # PASSENGERS
    # =========================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passengers (

            passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,

            full_name TEXT NOT NULL,

            gender TEXT,

            date_of_birth TEXT,

            nationality TEXT,

            phone TEXT,

            email TEXT,

            passport_number TEXT UNIQUE,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # =========================================================
    # BOOKINGS
    # =========================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (

            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,

            booking_reference TEXT UNIQUE,

            passenger_id INTEGER,

            flight_id INTEGER,

            booking_date TEXT DEFAULT CURRENT_TIMESTAMP,

            seat_number TEXT,

            travel_class TEXT DEFAULT 'Economy',

            booking_status TEXT DEFAULT 'Pending',

            total_amount REAL,

            FOREIGN KEY(passenger_id)
                REFERENCES passengers(passenger_id)
                ON DELETE CASCADE,

            FOREIGN KEY(flight_id)
                REFERENCES flights(flight_id)
                ON DELETE CASCADE
        )
    """)

    # =========================================================
    # PAYMENTS
    # =========================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (

            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,

            booking_id INTEGER,

            payment_method TEXT,

            payment_status TEXT DEFAULT 'Pending',

            amount REAL,

            transaction_code TEXT,

            paid_at TEXT,

            FOREIGN KEY(booking_id)
                REFERENCES bookings(booking_id)
                ON DELETE CASCADE
        )
    """)

    # =========================================================
    # TICKETS
    # =========================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (

            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,

            booking_id INTEGER,

            ticket_number TEXT UNIQUE,

            pnr_code TEXT UNIQUE,

            issue_date TEXT DEFAULT CURRENT_TIMESTAMP,

            qr_data TEXT,

            FOREIGN KEY(booking_id)
                REFERENCES bookings(booking_id)
                ON DELETE CASCADE
        )
    """)

    # =========================================================
    # SEATS
    # =========================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seats (

            seat_id INTEGER PRIMARY KEY AUTOINCREMENT,

            flight_id INTEGER,

            seat_number TEXT,

            seat_class TEXT DEFAULT 'Economy',

            is_reserved INTEGER DEFAULT 0,

            passenger_id INTEGER,

            FOREIGN KEY(flight_id)
                REFERENCES flights(flight_id)
                ON DELETE CASCADE,

            FOREIGN KEY(passenger_id)
                REFERENCES passengers(passenger_id)
                ON DELETE SET NULL
        )
    """)

    # =========================================================
    # EMAIL LOGS
    # =========================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_logs (

            email_log_id INTEGER PRIMARY KEY AUTOINCREMENT,

            passenger_id INTEGER,

            recipient_email TEXT,

            email_type TEXT,

            sent_at TEXT DEFAULT CURRENT_TIMESTAMP,

            status TEXT,

            FOREIGN KEY(passenger_id)
                REFERENCES passengers(passenger_id)
                ON DELETE CASCADE
        )
    """)

    # =========================================================
    # SYSTEM SETTINGS
    # =========================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (

            setting_id INTEGER PRIMARY KEY AUTOINCREMENT,

            setting_key TEXT UNIQUE,

            setting_value TEXT
        )
    """)

    # =========================================================
    # DEFAULT ADMIN ACCOUNT
    # =========================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM accounts
    """)

    count = cursor.fetchone()[0]

    if count == 0:

        password_hash = hashlib.sha256(
            "admin123".encode()
        ).hexdigest()

        cursor.execute("""
            INSERT INTO accounts (

                username,
                email,
                password_hash,
                full_name,
                role

            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            "admin",
            "admin@jetjetair.com",
            password_hash,
            "JetJet Administrator",
            "admin"
        ))

        print("✅ Default admin created")
        print("Username: admin")
        print("Password: admin123")

    conn.commit()

    conn.close()

    print("\n✅ Database initialized successfully!")
    print("""
Tables created:

- accounts
- flights
- passengers
- bookings
- payments
- tickets
- seats
- email_logs
- system_settings
""")


if __name__ == "__main__":

    init_db()