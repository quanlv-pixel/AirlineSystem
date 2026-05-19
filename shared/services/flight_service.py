from database.db import get_connection as connect_db
from shared.models.flight import Flight


def _row_to_flight(row: tuple) -> Flight:
    return Flight(
        flight_id=row[0],
        flight_number=row[1],
        airline_name=row[2],
        departure=row[3],
        destination=row[4],
        departure_time=row[5],
        arrival_time=row[6],
        available_seats=row[7],
        total_seats=row[8],
        ticket_price=row[9],
        status=row[10],
        aircraft=row[11],
        gate=row[12],
        terminal=row[13],
        created_at=row[14],
    )


def get_all_flights() -> list[Flight]:
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM flights
        ORDER BY departure_time
    """)

    rows = cursor.fetchall()

    conn.close()

    return [_row_to_flight(row) for row in rows]


def get_flight_by_id(flight_id: int) -> Flight | None:
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM flights
        WHERE flight_id = ?
    """, (flight_id,))

    row = cursor.fetchone()

    conn.close()

    return _row_to_flight(row) if row else None


def create_flight(
    flight_number: str,
    airline_name: str,
    departure: str,
    destination: str,
    departure_time: str,
    arrival_time: str,
    total_seats: int,
    ticket_price: float,
    aircraft: str = None,
    gate: str = None,
    terminal: str = None,
) -> tuple[bool, str]:

    if departure == destination:
        return False, "Departure and destination cannot be the same."

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO flights (
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
                terminal
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            flight_number,
            airline_name,
            departure,
            destination,
            departure_time,
            arrival_time,
            total_seats,
            total_seats,
            ticket_price,
            "scheduled",
            aircraft,
            gate,
            terminal,
        ))

        conn.commit()

        return True, "Flight created successfully."

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()


def update_flight(
    flight_id: int,
    departure_time: str = None,
    arrival_time: str = None,
    ticket_price: float = None,
    status: str = None,
) -> bool:

    conn = connect_db()
    cursor = conn.cursor()

    try:
        if departure_time:
            cursor.execute("""
                UPDATE flights
                SET departure_time = ?
                WHERE flight_id = ?
            """, (departure_time, flight_id))

        if arrival_time:
            cursor.execute("""
                UPDATE flights
                SET arrival_time = ?
                WHERE flight_id = ?
            """, (arrival_time, flight_id))

        if ticket_price is not None:
            cursor.execute("""
                UPDATE flights
                SET ticket_price = ?
                WHERE flight_id = ?
            """, (ticket_price, flight_id))

        if status:
            cursor.execute("""
                UPDATE flights
                SET status = ?
                WHERE flight_id = ?
            """, (status, flight_id))

        conn.commit()

        return True

    finally:
        conn.close()


def delete_flight(flight_id: int) -> bool:
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM flights
            WHERE flight_id = ?
        """, (flight_id,))

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()


def get_total_flights() -> int:
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM flights
    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total

def get_average_load_factor() -> int:
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            AVG(
                (
                    CAST(total_seats - available_seats AS FLOAT)
                    / total_seats
                ) * 100
            )
        FROM flights
        WHERE total_seats > 0
    """)

    result = cursor.fetchone()[0]

    conn.close()

    if result is None:
        return 0

    return round(result)

def sync_mock_flight_to_db(flight_id: int) -> bool:
    """
    Checks if a flight exists in the database. If not, fetches it from
    the aviation API (mock) and inserts it into the local database.
    """
    from shared.api.aviation_api import fetch_live_flights

    flight = get_flight_by_id(flight_id)
    if flight:
        return True

    # Flight not in DB, try to find it in mock API
    all_mock = fetch_live_flights()
    mock_flight = next((f for f in all_mock if f["flight_id"] == flight_id), None)

    if not mock_flight:
        return False

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO flights (
                flight_id, flight_number, airline_name, departure, destination,
                departure_time, arrival_time, available_seats, total_seats,
                ticket_price, status, aircraft, gate, terminal
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mock_flight["flight_id"],
            mock_flight["flight_number"],
            mock_flight["airline_name"],
            mock_flight["departure"],
            mock_flight["destination"],
            mock_flight["departure_time"],
            mock_flight["arrival_time"],
            mock_flight["available_seats"],
            mock_flight["total_seats"],
            mock_flight["ticket_price"],
            mock_flight["status"],
            mock_flight["aircraft"],
            mock_flight["gate"],
            mock_flight["terminal"]
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"[flight_service] Error syncing flight {flight_id}: {e}")
        return False
    finally:
        conn.close()