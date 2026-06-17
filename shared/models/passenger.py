class Passenger:
    def __init__(
        self,
        passenger_id: int = None,
        full_name: str = None,
        gender: str = None,
        date_of_birth: str = None,
        nationality: str = None,
        phone: str = None,
        email: str = None,

        member_rank: str = "member",
        total_spending: float = 0,

        passport_number: str = None,
        emergency_contact: str = None,
        created_at: str = None,
        month: int = None,  # <-- THÊM THUỘC TÍNH NÀY
    ):
        self.passenger_id = passenger_id
        self.full_name = full_name
        self.gender = gender
        self.date_of_birth = date_of_birth
        self.nationality = nationality
        self.phone = phone
        self.email = email

        self.member_rank = member_rank
        self.total_spending = total_spending

        self.passport_number = passport_number
        self.emergency_contact = emergency_contact
        self.created_at = created_at
        self.month = month  # <-- GÁN GIÁ TRỊ NÀY

    def __repr__(self):
        return (
            f"Passenger("
            f"id={self.passenger_id}, "
            f"name='{self.full_name}', "
            f"rank='{self.member_rank}', "
            f"spending={self.total_spending}"
            f")"
        )