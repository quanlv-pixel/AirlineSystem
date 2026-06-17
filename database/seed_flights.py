"""
database/seed_flights.py
---------------------------------
Seed dữ liệu chuyến bay mặc định
"""

import sqlite3
import os
import random
# Sửa import: Lấy từ mock_data
from shared.mock_data import MOCK_FLIGHTS

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "airline.db"
)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def seed_flights():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM flights")
    count = cursor.fetchone()[0]

    if count > 0:
        conn.close()
        print("Flights already exist")
        return

    used_numbers = set()

    for index, f in enumerate(MOCK_FLIGHTS, start=1):
        # Sửa cú pháp: Dùng f.thuộc_tính thay vì f["..."]
        # Thêm giá trị mặc định tránh lỗi NOT NULL
        original = f.flight_number or f"JJ{index:03d}"
        dep = f.departure or "SGN"
        dst = f.destination or "HAN"

        # Nếu trùng thì tạo mã mới
        if original in used_numbers:
            new_number = f"JJ{dep}{dst}{index:03d}"
            f.flight_number = new_number

        used_numbers.add(f.flight_number)

        cursor.execute("""
            INSERT INTO flights(
                flight_number,
                airline_name,
                departure,
                destination,
                departure_time,
                arrival_time,
                available_seats,
                total_seats,
                ticket_price,
                status,
                aircraft,
                gate,
                terminal,
                delay_minutes,
                flight_duration,
                weather_status
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            f.flight_number,
            f.airline_name or "JetJet Air",
            dep,
            dst,
            # Cấp ngày giờ giả lập để không bị dính lỗi NOT NULL
            f.departure_time or f"2026-06-18 {random.randint(6, 18):02d}:00:00",
            f.arrival_time or f"2026-06-18 {random.randint(19, 23):02d}:30:00",
            f.available_seats if f.available_seats is not None else 150,
            f.total_seats or 180,
            f.ticket_price or 120.0,
            f.status or "Scheduled",
            f.aircraft or "A320",
            f.gate or "G1",
            f.terminal or "T1",
            0,             # delay_minutes
            120,           # flight_duration
            "Normal"       # weather_status
        ))

    conn.commit()
    conn.close()

    print(f"✅ Seeded {len(MOCK_FLIGHTS)} flights")