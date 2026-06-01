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
        promo_used=row["promo_used"] if "promo_used" in row.keys() else None,
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
    created_by: str = None,
    promo_used: str = None,
) -> tuple[bool, str, int | None]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO bookings (
                booking_reference, passenger_id, flight_id, seat_number,
                booking_class, total_amount, payment_status, booking_status,
                created_by, promo_used
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (booking_reference, passenger_id, flight_id, seat_number,
              booking_class, total_amount, payment_status, booking_status,
              created_by, promo_used))
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

def get_booking_history_by_user(username: str):
    """
    Fetches booking history for a specific user.
    Joins with flights to get route and time information.
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Based on init_db.py schema: 
    # bookings table has: booking_id, booking_date, total_amount, booking_status, created_by, seat_number
    # flights table has: flight_id, flight_number, departure, destination, departure_time, arrival_time
    query = """
        SELECT b.booking_id, b.booking_date, b.total_amount, b.booking_status as status,
               f.flight_number as flight_code, f.departure, f.destination, f.departure_time, f.arrival_time,
               b.seat_number as seats
        FROM bookings b
        JOIN flights f ON b.flight_id = f.flight_id
        WHERE b.created_by = ?
        ORDER BY b.booking_id DESC
    """
    try:
        cursor.execute(query, (username,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[Service Error] get_booking_history_by_user: {e}")
        return []
    finally:
        conn.close()
