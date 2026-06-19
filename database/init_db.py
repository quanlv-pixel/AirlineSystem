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
from database.seed_flights import seed_flights
from shared.mock_data import SEED_AIRPORTS, SEED_PASSENGERS, SEED_ACCOUNTS

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
            role TEXT NOT NULL DEFAULT 'customer',
            phone TEXT,
            is_activated INTEGER DEFAULT 0,
            balance REAL DEFAULT 0.0, 
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
            flight_number TEXT UNIQUE NOT NULL,
            airline_name TEXT NOT NULL,
            departure TEXT NOT NULL,
            destination TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            arrival_time TEXT NOT NULL,
            available_seats INTEGER NOT NULL DEFAULT 180,
            total_seats INTEGER NOT NULL DEFAULT 180,
            ticket_price REAL NOT NULL,
            status TEXT DEFAULT 'Scheduled',
            aircraft TEXT,
            gate TEXT,
            terminal TEXT,
            delay_minutes INTEGER DEFAULT 0,
            flight_duration INTEGER DEFAULT 0,
            weather_status TEXT,
            flight_type TEXT DEFAULT 'Domestic',
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
            gender TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            nationality TEXT,
            phone TEXT,
            email TEXT,
            member_rank TEXT DEFAULT 'member',
            passport_number TEXT UNIQUE,
            total_spending REAL DEFAULT 0,
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
            seat_number TEXT,
            booking_class TEXT DEFAULT 'Economy',
            total_amount REAL,
            payment_status TEXT DEFAULT 'Pending',
            booking_status TEXT DEFAULT 'Pending',
            promo_used TEXT DEFAULT NULL,
            booking_date TEXT DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
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
            seat_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_id    INTEGER NOT NULL,
            seat_number  TEXT NOT NULL,
            seat_class   TEXT DEFAULT 'Economy',
            is_reserved  INTEGER DEFAULT 0,
            passenger_id INTEGER,
            created_at   TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(flight_id)
                REFERENCES flights(flight_id),

            FOREIGN KEY(passenger_id)
                REFERENCES passengers(passenger_id)
        )
    """)

    # =========================================================
    # AIRPORTS
    # =========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS airports(
            airport_code TEXT PRIMARY KEY,
            airport_name TEXT,
            city TEXT,
            country TEXT
        )
        """)
    
    cursor.executemany("""
        INSERT OR IGNORE INTO airports
        VALUES(?,?,?,?)
        """, SEED_AIRPORTS)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flight_delays(
        delay_id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_id INTEGER,
        reason TEXT,
        delay_minutes INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(flight_id)
        REFERENCES flights(flight_id)
        ON DELETE CASCADE
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flight_logs(
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_id INTEGER,
        action TEXT,
        created_by TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(flight_id)
        REFERENCES flights(flight_id)
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

    # =========================================================
    # SAFE MIGRATIONS
    # =========================================================
    cursor.execute("PRAGMA table_info(accounts)")
    accounts_cols = [row[1] for row in cursor.fetchall()]
    if "is_activated" not in accounts_cols:
        cursor.execute("ALTER TABLE accounts ADD COLUMN is_activated INTEGER DEFAULT 0")

    cursor.execute("PRAGMA table_info(bookings)")
    bookings_cols = [row[1] for row in cursor.fetchall()]
    if "promo_used" not in bookings_cols:
        cursor.execute("ALTER TABLE bookings ADD COLUMN promo_used TEXT DEFAULT NULL")

    conn.commit()
    conn.close()

    seed_flights()
    _seed_passengers_and_accounts()

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
- flight_logs
- system_settings
""")



def _seed_passengers_and_accounts():
    """
    Inserts realistic Vietnamese passenger profiles and matching customer
    accounts if they don't already exist. Covers all 4 spending tiers
    with a mix of activated (is_activated=1) and non-activated accounts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # passenger + account data imported from shared/mock_data.py
    passengers = SEED_PASSENGERS
    accounts   = SEED_ACCOUNTS


    try:
        # Insert passengers (skip duplicates by passport_number)
        for p in passengers:
            cursor.execute("""
                INSERT OR IGNORE INTO passengers
                    (full_name, gender, date_of_birth, nationality, phone, email,
                     member_rank, passport_number, total_spending)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, p)

        # Insert customer accounts (skip duplicates by username)
        for (uname, email, fname, pwd, activated) in accounts:
            ph = hashlib.sha256(pwd.encode()).hexdigest()
            cursor.execute("""
                INSERT OR IGNORE INTO accounts
                    (username, email, password_hash, full_name, role, is_activated)
                VALUES (?, ?, ?, ?, 'customer', ?)
            """, (uname, email, ph, fname, activated))

        conn.commit()
        print("✅ Passenger seed data inserted/verified.")
    except Exception as e:
        print(f"⚠️  Seed error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    