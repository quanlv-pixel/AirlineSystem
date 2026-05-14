from database.db import get_connection

from models.booking import Booking


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

    cursor.execute("""
        SELECT *
        FROM bookings
        ORDER BY booking_date DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return [
        row_to_booking(row)
        for row in rows
    ]


def get_active_bookings_count():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE booking_status = 'Confirmed'
    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total


def get_total_revenue():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(total_amount)
        FROM bookings
        WHERE payment_status = 'Paid'
    """)

    result = cursor.fetchone()[0]

    conn.close()

    return result if result else 0