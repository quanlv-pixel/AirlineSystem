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
        date_of_birth=row[3],
        nationality=row[4],
        phone=row[5],
        email=row[6],

        member_rank=row[7],      # thêm
        passport_number=row[8],
        total_spending=row[9],   # thêm

        created_at=row[10],
    )


# ─────────────────────────────────────────────
# CRUD
# ─────────────────────────────────────────────

def create_passenger(
    full_name: str,
    gender: str,
    date_of_birth: str,
    phone: str,
    passport_number: str,
    email: str,
    nationality: str,
    member_rank: str = "member",
) -> tuple[bool, str, int | None]:

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO passengers (
                full_name,
                gender,
                date_of_birth,
                phone,
                passport_number,
                email,
                nationality,
                member_rank
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            full_name,
            gender,
            date_of_birth,
            phone,
            passport_number,
            email,
            nationality,
            member_rank,
        ))

        conn.commit()
        new_id = cursor.lastrowid
        return True, "Passenger created successfully.", new_id

    except Exception as e:
        return False, str(e), None

    finally:
        conn.close()


def get_all_passengers() -> list[Passenger]:
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            passenger_id, full_name, gender, date_of_birth, nationality,
            phone, email, member_rank, passport_number, total_spending, created_at
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
            passenger_id, full_name, gender, date_of_birth, nationality,
            phone, email, member_rank, passport_number, total_spending, created_at
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
            passenger_id, full_name, gender, date_of_birth, nationality,
            phone, email, member_rank, passport_number, total_spending, created_at
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
    date_of_birth: str,
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
            date_of_birth = ?,
            phone = ?,
            passport_number = ?,
            email = ?,
            nationality = ?,
            member_rank = ?
        WHERE passenger_id = ?
    """, (
        full_name,
        gender,
        date_of_birth,
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
    """Atomically add *amount* to the passenger's total_spending.
    COALESCE guards against a NULL baseline (new passengers have NULL spending).
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE passengers
        SET total_spending = COALESCE(total_spending, 0) + ?
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


# ─────────────────────────────────────────────
# ENRICHED (with is_activated from accounts)
# ─────────────────────────────────────────────

class PassengerEnriched(Passenger):
    """Passenger with is_activated field joined from accounts table."""
    def __init__(self, *args, is_activated: int = 0, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_activated = is_activated


def _row_to_enriched(row) -> PassengerEnriched:
    p = PassengerEnriched(
        passenger_id=row[0],
        full_name=row[1],
        gender=row[2],
        date_of_birth=row[3],
        nationality=row[4],
        phone=row[5],
        email=row[6],
        member_rank=row[7],
        passport_number=row[8],
        total_spending=row[9],
        created_at=row[10],
        is_activated=int(row[11]) if row[11] is not None else 0,
    )
    return p


def get_all_passengers_enriched() -> list[PassengerEnriched]:
    """
    Returns all passengers with is_activated joined from accounts on email.
    Used by management_app to show/hide tier badges based on VIP activation.
    """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            p.passenger_id, p.full_name, p.gender, p.date_of_birth, p.nationality,
            p.phone, p.email, p.member_rank, p.passport_number, p.total_spending,
            p.created_at,
            COALESCE(a.is_activated, 0) AS is_activated
        FROM passengers p
        LEFT JOIN accounts a ON LOWER(p.email) = LOWER(a.email)
        ORDER BY p.passenger_id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_enriched(row) for row in rows]


def search_passengers_enriched(keyword: str) -> list[PassengerEnriched]:
    """Enriched passenger search (includes is_activated)."""
    conn = connect_db()
    cursor = conn.cursor()
    q = f"%{keyword}%"
    cursor.execute("""
        SELECT
            p.passenger_id, p.full_name, p.gender, p.date_of_birth, p.nationality,
            p.phone, p.email, p.member_rank, p.passport_number, p.total_spending,
            p.created_at,
            COALESCE(a.is_activated, 0) AS is_activated
        FROM passengers p
        LEFT JOIN accounts a ON LOWER(p.email) = LOWER(a.email)
        WHERE p.full_name LIKE ? OR p.email LIKE ? OR p.passport_number LIKE ?
        ORDER BY p.passenger_id DESC
    """, (q, q, q))
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_enriched(row) for row in rows]
