"""
shared/api/mock_api.py
-----------------------
Enhanced Mock Data and Operational Simulation for JetJet Air.
Includes international hubs, expanded flight volume, and diverse statuses.
"""
from __future__ import annotations
import random
from datetime import datetime, timedelta

# ── Expanded Airport List ───────────────────────────────────────────────────
AIRPORTS = {
    "SGN": "Ho Chi Minh City",
    "HAN": "Ha Noi",
    "DAD": "Da Nang",
    "CXR": "Nha Trang",
    "PQC": "Phu Quoc",
    "SIN": "Singapore",
    "BKK": "Bangkok",
    "ICN": "Seoul",
    "NRT": "Tokyo",
    "LHR": "London",
    "JFK": "New York",
    "SYD": "Sydney"
}

# ── Enhanced Mock Weather Data ───────────────────────────────────────────────
# Added extreme conditions and varied delay risks
MOCK_WEATHER = {
    "SGN": {"temp": 32, "condition": "Sunny", "delay_risk": "Low"},
    "HAN": {"temp": 18, "condition": "Heavy Fog", "delay_risk": "High"},
    "DAD": {"temp": 28, "condition": "Partly Cloudy", "delay_risk": "Low"},
    "CXR": {"temp": 30, "condition": "Breezy", "delay_risk": "Low"},
    "PQC": {"temp": 29, "condition": "Typhoon", "delay_risk": "Critical"},
    "SIN": {"temp": 31, "condition": "Rainy", "delay_risk": "Medium"},
    "BKK": {"temp": 34, "condition": "Sunny", "delay_risk": "Low"},
    "ICN": {"temp": -5, "condition": "Snowstorm", "delay_risk": "High"},
    "NRT": {"temp": 12, "condition": "Cloudy", "delay_risk": "Medium"},
    "LHR": {"temp": 10, "condition": "Drizzle", "delay_risk": "Medium"},
    "JFK": {"temp": 22, "condition": "Clear", "delay_risk": "Low"},
    "SYD": {"temp": 25, "condition": "Sunny", "delay_risk": "Low"},
}

# ── Occupancy rules theo status ──────────────────────────────────────────────
# Đã khởi hành (không đặt được):   Delayed, In Air, Gate Closed  → 90-100%
# Chưa khởi hành (còn đặt được):   Scheduled, Boarding           → 0-69%
# Hủy:                              Canceled                      → 0%
# Hoàn thành:                       Completed                     → 90-100%
_OCCUPANCY_RANGES = {
    "Scheduled":  (5,  69),   # Còn bán vé, chưa đầy
    "Boarding":   (30, 68),   # Đang lên máy, hầu hết đã check-in nhưng chưa max
    "Delayed":    (90, 100),  # Đã khởi hành trễ, vé đã bán gần/đầy
    "In Air":     (92, 100),  # Đang bay, vé đã đóng
    "Gate Closed":(95, 100),  # Cổng đã đóng
    "Canceled":   (0,  0),    # Hủy → không hành khách
    "Completed":  (90, 100),  # Hoàn thành → đã đầy khách
}
# Các status mà hành khách KHÔNG thể đặt vé (chuyến đã khởi hành hoặc đóng)
STATUSES_NOT_BOOKABLE = {"Delayed", "In Air", "Gate Closed", "Canceled", "Completed"}


# ── Enhanced Flight Generation ───────────────────────────────────────────────
def _generate_enhanced_flights(count: int = 50):
    airlines = ["JetJet Air", "Global Connect", "Sky High", "Pacific Way"]
    aircrafts = ["Airbus A321 Neo", "Boeing 787-9", "Airbus A350-1000", "Boeing 737 MAX"]
    airport_codes = list(AIRPORTS.keys())

    statuses = [
        ("Scheduled",  0.45),
        ("Boarding",   0.15),
        ("Delayed",    0.15),
        ("In Air",     0.10),
        ("Gate Closed",0.05),
        ("Canceled",   0.05),
        ("Completed",  0.05),
    ]

    flights = []
    now = datetime.now()
    rng = random.Random(42)

    for i in range(1, count + 1):
        dep = rng.choice(airport_codes)
        dst = rng.choice([a for a in airport_codes if a != dep])

        time_offset = rng.randint(-12, 48)
        dep_time = now + timedelta(hours=time_offset)
        duration = rng.randint(90, 720)
        arr_time = dep_time + timedelta(minutes=duration)

        status_choice = rng.choices(
            [s[0] for s in statuses],
            weights=[s[1] for s in statuses]
        )[0]

        # Tính occupancy_percent theo đúng range của status
        lo, hi = _OCCUPANCY_RANGES.get(status_choice, (10, 80))
        occupancy = lo if lo == hi else rng.randint(lo, hi)

        total_seats = 180
        # available_seats tính ngược từ occupancy để nhất quán
        reserved_count = round(total_seats * occupancy / 100)
        available_seats = total_seats - reserved_count

        is_intl = dep not in ("SGN","HAN","DAD","CXR","PQC") or dst not in ("SGN","HAN","DAD","CXR","PQC")
        price = float(rng.randint(150, 1200) if is_intl else rng.randint(50, 300))

        flights.append({
            "flight_id":       i,
            "flight_number":   f"JJ{rng.randint(100, 999)}",
            "airline_name":    rng.choice(airlines),
            "departure":       dep,
            "destination":     dst,
            "departure_time":  dep_time.strftime("%Y-%m-%d %H:%M"),
            "arrival_time":    arr_time.strftime("%Y-%m-%d %H:%M"),
            "aircraft":        rng.choice(aircrafts),
            "terminal":        rng.choice(["T1", "T2", "INTL"]),
            "gate":            f"{rng.choice(['A','B','C','D'])}{rng.randint(1,40)}",
            "total_seats":     total_seats,
            "available_seats": available_seats,
            "occupancy_percent": occupancy,    # ← Trường mới, dùng cho flights_page
            "ticket_price":    price,
            "status":          status_choice,
        })
    return flights

MOCK_FLIGHTS = _generate_enhanced_flights(60) # Generate 60 for richness

# ── Mock Seat Data ──────────────────────────────────────────────────────────
def get_mock_seat_map(flight_id: int) -> list[str]:
    """
    Trả về danh sách ghế đã đặt cho flight_id, phân bổ random nhất quán.
    Tỷ lệ ghế đặt = occupancy_percent của chuyến bay tương ứng.
    Nếu không tìm thấy flight, fallback về 30%.
    """
    # Tìm flight trong MOCK_FLIGHTS để lấy occupancy_percent
    target = next((f for f in MOCK_FLIGHTS if f["flight_id"] == flight_id), None)
    occupancy_pct = target["occupancy_percent"] if target else 30

    total_rows = 35
    cols = ["A", "B", "C", "D", "E", "F"]
    total_seats = total_rows * len(cols)          # 210 seats
    target_reserved = round(total_seats * occupancy_pct / 100)

    # Dùng seed cố định theo flight_id để kết quả nhất quán mỗi lần gọi
    rng = random.Random(flight_id * 7 + 13)
    all_seats = [(r, c) for r in range(1, total_rows + 1) for c in cols]
    rng.shuffle(all_seats)

    reserved_seats = all_seats[:target_reserved]
    return [f"{r}{c}" for r, c in reserved_seats]