"""
database/seed_flights.py
---------------------------------
Seed dữ liệu chuyến bay mặc định
"""

import sqlite3
import os
from shared.api.mock_api import MOCK_FLIGHTS


DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "airline.db"
)


def get_connection():

    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        "PRAGMA foreign_keys=ON"
    )

    return conn


def seed_flights():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM flights"
    )

    count = cursor.fetchone()[0]

    if count > 0:
        conn.close()
        print("Flights already exist")
        return


    used_numbers = set()

    for index, f in enumerate(MOCK_FLIGHTS, start=1):

        original = f["flight_number"]

        # Nếu trùng thì tạo mã mới
        if original in used_numbers:

            dep = f["departure"]
            dst = f["destination"]

            new_number = f"JJ{dep}{dst}{index:03d}"

            f["flight_number"] = new_number

        used_numbers.add(
            f["flight_number"]
        )

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

        VALUES(
        ?,?,?,?,?,?,
        ?,?,?,?,?,?,
        ?,?,?,?
        )

        """,(

            f["flight_number"],
            f["airline_name"],
            f["departure"],
            f["destination"],
            f["departure_time"],
            f["arrival_time"],
            f["available_seats"],
            f["total_seats"],
            f["ticket_price"],
            f["status"],
            f["aircraft"],
            f["gate"],
            f["terminal"],

            0,
            120,
            "Normal"
        ))

    conn.commit()
    conn.close()

    print(f"✅ Seeded {len(MOCK_FLIGHTS)} flights")