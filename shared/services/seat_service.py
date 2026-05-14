from database.db import get_connection as connect_db
from models.seat import Seat


def _row_to_seat(row: tuple) -> Seat:
    return Seat(
        seat_id=row[0],
        flight_id=row[1],
        seat_number=row[2],
        seat_class=row[3],
        is_reserved=bool(row[4]),
        passenger_id=row[5],
        created_at=row[6],
    )


def create_seat(
    flight_id: int,
    seat_number: str,
    seat_class: str = "Economy",
) -> tuple[bool, str]:

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO seats (
                flight_id,
                seat_number,
                seat_class,
                is_reserved
            )
            VALUES (?, ?, ?, ?)
        """, (
            flight_id,
            seat_number,
            seat_class,
            0,
        ))

        conn.commit()

        return True, "Seat created successfully."

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()


def create_seats_for_flight(
    flight_id: int,
    rows: int = 10,
    seats_per_row: list = ["A", "B", "C", "D", "E", "F"],
) -> tuple[bool, str]:

    conn = connect_db()
    cursor = conn.cursor()

    try:
        for row in range(1, rows + 1):

            for letter in seats_per_row:

                seat_number = f"{row}{letter}"

                seat_class = "Economy"

                if row <= 2:
                    seat_class = "Business"

                cursor.execute("""
                    INSERT INTO seats (
                        flight_id,
                        seat_number,
                        seat_class,
                        is_reserved
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    flight_id,
                    seat_number,
                    seat_class,
                    0,
                ))

        conn.commit()

        return True, "Seats generated successfully."

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()


def get_seats_by_flight(
    flight_id: int
) -> list[Seat]:

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM seats
        WHERE flight_id = ?
        ORDER BY seat_number
    """, (flight_id,))

    rows = cursor.fetchall()

    conn.close()

    return [_row_to_seat(row) for row in rows]


def get_available_seats(
    flight_id: int
) -> list[Seat]:

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM seats
        WHERE flight_id = ?
        AND is_reserved = 0
        ORDER BY seat_number
    """, (flight_id,))

    rows = cursor.fetchall()

    conn.close()

    return [_row_to_seat(row) for row in rows]


def reserve_seat(
    flight_id: int,
    seat_number: str,
    passenger_id: int,
) -> tuple[bool, str]:

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT is_reserved
            FROM seats
            WHERE flight_id = ?
            AND seat_number = ?
        """, (
            flight_id,
            seat_number,
        ))

        row = cursor.fetchone()

        if not row:
            return False, "Seat not found."

        if row[0] == 1:
            return False, "Seat already reserved."

        cursor.execute("""
            UPDATE seats
            SET is_reserved = 1,
                passenger_id = ?
            WHERE flight_id = ?
            AND seat_number = ?
        """, (
            passenger_id,
            flight_id,
            seat_number,
        ))

        conn.commit()

        return True, "Seat reserved successfully."

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()


def release_seat(
    flight_id: int,
    seat_number: str,
) -> bool:

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE seats
            SET is_reserved = 0,
                passenger_id = NULL
            WHERE flight_id = ?
            AND seat_number = ?
        """, (
            flight_id,
            seat_number,
        ))

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()


def get_reserved_seats_count(
    flight_id: int
) -> int:

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM seats
        WHERE flight_id = ?
        AND is_reserved = 1
    """, (flight_id,))

    total = cursor.fetchone()[0]

    conn.close()

    return total