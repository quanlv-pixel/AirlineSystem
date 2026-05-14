from database.db import get_connection as connect_db
from shared.models.passenger import Passenger


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _row_to_passenger(row) -> Passenger:

    return Passenger(
        passenger_id=row[0],
        full_name=row[1],
        gender=row[2],
        phone=row[3],
        passport_number=row[4],
        email=row[5],
        nationality=row[6],
        member_rank=row[7],
        total_spending=row[8],
        created_at=row[9],
    )


# ─────────────────────────────────────────────
# CRUD
# ─────────────────────────────────────────────

def create_passenger(
    full_name: str,
    gender: str,
    phone: str,
    passport_number: str,
    email: str,
    nationality: str,
    member_rank: str = "member",
) -> tuple[bool, str]:

    conn = connect_db()

    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO passengers (
                full_name,
                gender,
                phone,
                passport_number,
                email,
                nationality,
                member_rank
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            full_name,
            gender,
            phone,
            passport_number,
            email,
            nationality,
            member_rank,
        ))

        conn.commit()

        return True, "Passenger created successfully."

    except Exception as e:

        return False, str(e)

    finally:

        conn.close()


def get_all_passengers() -> list[Passenger]:

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            passenger_id,
            full_name,
            gender,
            phone,
            passport_number,
            email,
            nationality,
            member_rank,
            total_spending,
            created_at
        FROM passengers
        ORDER BY passenger_id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return [_row_to_passenger(row) for row in rows]


def get_passenger_by_id(
    passenger_id: int
) -> Passenger | None:

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            passenger_id,
            full_name,
            gender,
            phone,
            passport_number,
            email,
            nationality,
            member_rank,
            total_spending,
            created_at
        FROM passengers
        WHERE passenger_id = ?
    """, (passenger_id,))

    row = cursor.fetchone()

    conn.close()

    if row:

        return _row_to_passenger(row)

    return None


def search_passengers(
    keyword: str
) -> list[Passenger]:

    conn = connect_db()

    cursor = conn.cursor()

    query = f"%{keyword}%"

    cursor.execute("""
        SELECT
            passenger_id,
            full_name,
            gender,
            phone,
            passport_number,
            email,
            nationality,
            member_rank,
            total_spending,
            created_at
        FROM passengers
        WHERE
            full_name LIKE ?
            OR email LIKE ?
            OR passport_number LIKE ?
    """, (
        query,
        query,
        query,
    ))

    rows = cursor.fetchall()

    conn.close()

    return [_row_to_passenger(row) for row in rows]


def update_passenger(
    passenger_id: int,
    full_name: str,
    gender: str,
    phone: str,
    passport_number: str,
    email: str,
    nationality: str,
    member_rank: str,
) -> bool:

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE passengers
        SET
            full_name = ?,
            gender = ?,
            phone = ?,
            passport_number = ?,
            email = ?,
            nationality = ?,
            member_rank = ?
        WHERE passenger_id = ?
    """, (
        full_name,
        gender,
        phone,
        passport_number,
        email,
        nationality,
        member_rank,
        passenger_id,
    ))

    conn.commit()

    updated = cursor.rowcount > 0

    conn.close()

    return updated


def update_spending(
    passenger_id: int,
    amount: float
):

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE passengers
        SET total_spending = total_spending + ?
        WHERE passenger_id = ?
    """, (
        amount,
        passenger_id,
    ))

    conn.commit()

    conn.close()


def delete_passenger(
    passenger_id: int
) -> bool:

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM passengers
        WHERE passenger_id = ?
    """, (passenger_id,))

    conn.commit()

    deleted = cursor.rowcount > 0

    conn.close()

    return deleted


def get_total_passengers() -> int:

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM passengers
    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total