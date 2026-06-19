
class Account:

    def __init__(
        self,
        account_id: int = None,
        username: str = None,
        email: str = None,
        password_hash: str = None,
        full_name: str = None,
        role: str = "staff",
        phone: str = None,
        created_at: str = None,
        last_login: str = None,
        is_activated: int = 0,
        balance: float = 0.0,
    ):
        self.account_id = account_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.role = role
        self.phone = phone
        self.created_at = created_at
        self.last_login = last_login
        self.is_activated = is_activated
        self.balance = balance

    @property
    def display_name(self) -> str:
        return self.full_name if self.full_name else self.username

    def is_admin(self) -> bool:
        return self.role == "admin"

    def __repr__(self) -> str:
        return (
            f"Account(id={self.account_id}, "
            f"username='{self.username}', "
            f"role='{self.role}')"
        )