class Payment:

    def __init__(
        self,
        payment_id: int = None,
        booking_id: int = None,
        payment_method: str = None,
        payment_amount: float = 0.0,
        payment_status: str = "Pending",
        transaction_code: str = None,
        paid_at: str = None,
    ):
        self.payment_id = payment_id

        self.booking_id = booking_id

        self.payment_method = payment_method

        self.payment_amount = payment_amount

        self.payment_status = payment_status

        self.transaction_code = transaction_code

        self.paid_at = paid_at

    def is_paid(self) -> bool:
        return self.payment_status == "Paid"

    def __repr__(self) -> str:
        return (
            f"Payment(id={self.payment_id}, "
            f"amount={self.payment_amount}, "
            f"status='{self.payment_status}')"
        )