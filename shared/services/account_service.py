import hashlib
from datetime import datetime

from database.db import get_connection as connect_db
from models.account import Account


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _row_to_account(row: tuple) -> Account:
    return Account(
        account_id=row[0],
        username=row[1],
        email=row[2],
        password_hash=row[3],
        full_name=row[4],
        role=row[5],
        created_at=row[6],
        last_login=row[7],
    )


# ─────────────────────────────────────────────────────────────────────────────
# Authentication
# ─────────────────────────────────────────────────────────────────────────────

def login(identifier: str, password: str) -> Account | None:
    conn = connect_db()
    cursor = conn.cursor()
    try:
        ph = hash_password(password)
        cursor.execute(
            """
            SELECT account_id, username, email, password_hash,
                   full_name, role, created_at, last_login
            FROM accounts
            WHERE (email = ? OR username = ?) AND password_hash = ?
            """,
            (identifier.strip().lower(), identifier.strip(), ph),
        )
        row = cursor.fetchone()
        if row:
            # Cập nhật last_login
            cursor.execute(
                "UPDATE accounts SET last_login = ? WHERE account_id = ?",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), row[0]),
            )
            conn.commit()
            return _row_to_account(row)
        return None
    finally:
        conn.close()


def create_account(
    username: str,
    email: str,
    password: str,
    full_name: str = None,
    role: str = "staff",
) -> tuple[bool, str]:
    
    # Validate cơ bản
    if not username or len(username) < 3:
        return False, "Username phải có ít nhất 3 ký tự."
    if not email or "@" not in email:
        return False, "Email không hợp lệ."
    if not password or len(password) < 6:
        return False, "Mật khẩu phải có ít nhất 6 ký tự."

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO accounts (username, email, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                username.strip(),
                email.strip().lower(),
                hash_password(password),
                full_name.strip() if full_name else None,
                role,
            ),
        )
        conn.commit()
        return True, "Tài khoản đã được tạo thành công!"
    except Exception as e:
        err = str(e)
        if "accounts.username" in err:
            return False, "Username đã tồn tại."
        if "accounts.email" in err:
            return False, "Email đã được đăng ký."
        return False, f"Lỗi: {err}"
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# CRUD
# ─────────────────────────────────────────────────────────────────────────────

def get_all_accounts() -> list[Account]:
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT account_id, username, email, password_hash,
               full_name, role, created_at, last_login
        FROM accounts
        ORDER BY account_id
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_account(r) for r in rows]


def get_account_by_id(account_id: int) -> Account | None:
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT account_id, username, email, password_hash,
               full_name, role, created_at, last_login
        FROM accounts WHERE account_id = ?
        """,
        (account_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return _row_to_account(row) if row else None


def update_account(
    account_id: int,
    full_name: str = None,
    role: str = None,
) -> bool:
    conn = connect_db()
    cursor = conn.cursor()
    try:
        if full_name is not None:
            cursor.execute(
                "UPDATE accounts SET full_name = ? WHERE account_id = ?",
                (full_name, account_id),
            )
        if role is not None:
            cursor.execute(
                "UPDATE accounts SET role = ? WHERE account_id = ?",
                (role, account_id),
            )
        conn.commit()
        return True
    finally:
        conn.close()


def update_password(account_id: int, new_password: str) -> bool:
    if len(new_password) < 6:
        return False
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE accounts SET password_hash = ? WHERE account_id = ?",
            (hash_password(new_password), account_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_account(account_id: int) -> bool:
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM accounts WHERE account_id = ?", (account_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()