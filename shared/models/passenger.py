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
        passport_number: str = None,
        emergency_contact: str = None,
        created_at: str = None,
    ):
        self.passenger_id = passenger_id

        self.full_name = full_name

        self.gender = gender

        self.date_of_birth = date_of_birth

        self.nationality = nationality

        self.phone = phone

        self.email = email

        self.passport_number = passport_number

        self.emergency_contact = emergency_contact

        self.created_at = created_at

    def __repr__(self) -> str:
        return (
            f"Passenger(id={self.passenger_id}, "
            f"name='{self.full_name}')"
        )