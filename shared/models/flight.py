class Flight:

    def __init__(
        self,
        flight_id: int = None,
        flight_number: str = None,
        airline_name: str = None,
        departure: str = None,
        destination: str = None,
        departure_time: str = None,
        arrival_time: str = None,
        aircraft: str = None,
        terminal: str = None,
        gate: str = None,
        total_seats: int = 0,
        available_seats: int = 0,
        ticket_price: float = 0.0,
        status: str = "Scheduled",
        created_at: str = None,
    ):
        self.flight_id = flight_id
        self.flight_number = flight_number
        self.airline_name = airline_name

        self.departure = departure
        self.destination = destination

        self.departure_time = departure_time
        self.arrival_time = arrival_time

        self.aircraft = aircraft

        self.terminal = terminal
        self.gate = gate

        self.total_seats = total_seats
        self.available_seats = available_seats

        self.ticket_price = ticket_price

        self.status = status

        self.created_at = created_at

    @property
    def route(self) -> str:
        return f"{self.departure} → {self.destination}"

    def is_full(self) -> bool:
        return self.available_seats <= 0

    def __repr__(self) -> str:
        return (
            f"Flight(id={self.flight_id}, "
            f"flight='{self.flight_number}', "
            f"route='{self.route}')"
        )