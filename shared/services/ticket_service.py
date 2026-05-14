from database.db import get_connection as connect_db


def generate_ticket(booking_id: int) -> tuple[bool, str]:

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT booking_reference
            FROM bookings
            WHERE booking_id = ?
        """, (booking_id,))

        row = cursor.fetchone()

        if not row:
            return False, "Booking not found."

        ticket_number = f"TKT-{row[0]}"

        cursor.execute("""
            INSERT INTO tickets (
                booking_id,
                ticket_number,
                issued_at
            )
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (
            booking_id,
            ticket_number,
        ))

        conn.commit()

        return True, ticket_number

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()