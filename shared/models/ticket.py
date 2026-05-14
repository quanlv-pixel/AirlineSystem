class Ticket:

    def __init__(
        self,
        ticket_id: int = None,
        booking_id: int = None,
        ticket_number: str = None,
        qr_code: str = None,
        issued_at: str = None,
    ):
        self.ticket_id = ticket_id

        self.booking_id = booking_id

        self.ticket_number = ticket_number

        self.qr_code = qr_code

        self.issued_at = issued_at

    def __repr__(self) -> str:
        return (
            f"Ticket(id={self.ticket_id}, "
            f"ticket='{self.ticket_number}')"
        )