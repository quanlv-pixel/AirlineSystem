class Booking:

    def __init__(
        self,
        booking_id: int = None,
        booking_reference: str = None,
        passenger_id: int = None,
        flight_id: int = None,
        seat_number: str = None,
        booking_class: str = "Economy",
        total_amount: float = 0.0,
        payment_status: str = "Pending",
        booking_status: str = "Pending",
        booking_date: str = None,
        created_by: int = None,
        promo_used: str = None,
    ):
        self.booking_id = booking_id
        self.booking_reference = booking_reference
        self.passenger_id = passenger_id
        self.flight_id = flight_id
        self.seat_number = seat_number
        self.booking_class = booking_class
        self.total_amount = total_amount
        self.payment_status = payment_status
        self.booking_status = booking_status
        self.booking_date = booking_date
        self.created_by = created_by
        self.promo_used = promo_used

    def is_paid(self) -> bool:
        return self.payment_status == "Paid"

    def is_confirmed(self) -> bool:
        return self.booking_status == "Confirmed"

    def __repr__(self) -> str:
        return (
            f"Booking(id={self.booking_id}, "
            f"reference='{self.booking_reference}', "
            f"status='{self.booking_status}')"
        )