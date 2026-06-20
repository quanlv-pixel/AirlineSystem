class Seat:

    def __init__(
        self,
        seat_id: int = None,
        flight_id: int = None,
        seat_number: str = None,
        seat_class: str = "Economy",
        is_reserved: int = 0,
        passenger_id: int = None, 
        created_at=None,
    ):
        self.seat_id = seat_id
        self.flight_id = flight_id
        self.seat_number = seat_number
        self.seat_class = seat_class
        self.created_at = created_at
        self.is_reserved = is_reserved
        self.passenger_id = passenger_id

    def is_available(self) -> bool:
        return self.is_reserved == 0

    def __repr__(self) -> str:
        return (
            f"Seat(id={self.seat_id}, "
            f"seat='{self.seat_number}', "
            f"class='{self.seat_class}', "
            f"passenger_id={self.passenger_id}, "
            f"created_at={self.created_at})"
        )