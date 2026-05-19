import sqlite3
import sys
from database.db import get_connection
from shared.models.booking import Booking

def row_to_booking(row):
    return Booking(
        booking_id=row["booking_id"],
        booking_reference=row["booking_reference"],
        passenger_id=row["passenger_id"],
        flight_id=row["flight_id"],
        seat_number=row["seat_number"],
        booking_class=row["booking_class"],
        total_amount=row["total_amount"],
        payment_status=row["payment_status"],
        booking_status=row["booking_status"],
        booking_date=row["booking_date"],
        created_by=row["created_by"],
    )

def get_all_bookings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings ORDER BY booking_date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [row_to_booking(row) for row in rows]

def create_booking(
    booking_reference: str,
    passenger_id: int,
    flight_id: int,
    seat_number: str,
    total_amount: float,
    booking_class: str = "Economy",
    payment_status: str = "Pending",
    booking_status: str = "Pending",
    created_by: str = None
) -> tuple[bool, str, int | None]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO bookings (
                booking_reference, passenger_id, flight_id, seat_number,
                booking_class, total_amount, payment_status, booking_status, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (booking_reference, passenger_id, flight_id, seat_number,
              booking_class, total_amount, payment_status, booking_status, created_by))
        conn.commit()
        new_id = cursor.lastrowid
        return True, "Booking created successfully.", new_id
    except Exception as e:
        return False, str(e), None
    finally:
        conn.close()

def get_total_bookings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bookings")
    total = cursor.fetchone()[0]
    conn.close()
    return total

def get_active_bookings_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE booking_status = 'Confirmed'")
    total = cursor.fetchone()[0]
    conn.close()
    return total

def get_total_revenue():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(total_amount) FROM bookings WHERE payment_status = 'Paid'")
    result = cursor.fetchone()[0]
    conn.close()
    return result if result else 0
