from database.db import get_connection as connect_db


def create_payment(
    booking_id: int,
    payment_method: str,
    amount: float,
    transaction_code: str,
) -> tuple[bool, str]:

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO payments (
                booking_id,
                payment_method,
                amount,
                payment_status,
                transaction_code
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            booking_id,
            payment_method,
            amount,
            "Paid",
            transaction_code,
        ))

        conn.commit()

        return True, "Payment completed."

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()