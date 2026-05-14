class Seat:

    def __init__(
        self,
        seat_id: int = None,
        flight_id: int = None,
        seat_number: str = None,
        seat_class: str = "Economy",
        is_reserved: int = 0,
    ):
        self.seat_id = seat_id

        self.flight_id = flight_id

        self.seat_number = seat_number

        self.seat_class = seat_class

        self.is_reserved = is_reserved

    def is_available(self) -> bool:
        return self.is_reserved == 0

    def __repr__(self) -> str:
        return (
            f"Seat(id={self.seat_id}, "
            f"seat='{self.seat_number}', "
            f"class='{self.seat_class}')"
        )