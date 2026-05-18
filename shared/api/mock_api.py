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

# ── Enhanced Flight Generation ───────────────────────────────────────────────
def _generate_enhanced_flights(count: int = 50):
    airlines = ["JetJet Air", "Global Connect", "Sky High", "Pacific Way"]
    aircrafts = ["Airbus A321 Neo", "Boeing 787-9", "Airbus A350-1000", "Boeing 737 MAX"]
    airport_codes = list(AIRPORTS.keys())
    
    statuses = [
        ("Scheduled", 0.60), 
        ("Delayed", 0.15), 
        ("Boarding", 0.10), 
        ("Gate Closed", 0.05), 
        ("Canceled", 0.05),
        ("In Air", 0.05)
    ]
    
    flights = []
    now = datetime.now()
    
    # Use a fixed seed for reproducible mocks if desired, or random for variety
    rng = random.Random(42) 
    
    for i in range(1, count + 1):
        dep = rng.choice(airport_codes)
        dst = rng.choice([a for a in airport_codes if a != dep])
        
        # Distribute flights over a 48 hour window
        time_offset = rng.randint(-12, 48) # Some in past, some in future
        dep_time = now + timedelta(hours=time_offset)
        duration = rng.randint(90, 720) # 1.5h to 12h flights
        arr_time = dep_time + timedelta(minutes=duration)
        
        # Weighted status selection
        status_choice = rng.choices([s[0] for s in statuses], weights=[s[1] for s in statuses])[0]
        
        flights.append({
            "flight_id": i,
            "flight_number": f"JJ{rng.randint(100, 999)}",
            "airline_name": rng.choice(airlines),
            "departure": dep,
            "destination": dst,
            "departure_time": dep_time.strftime("%Y-%m-%d %H:%M"),
            "arrival_time": arr_time.strftime("%Y-%m-%d %H:%M"),
            "aircraft": rng.choice(aircrafts),
            "terminal": rng.choice(["T1", "T2", "INTL"]),
            "gate": f"{rng.choice(['A','B','C','D'])}{rng.randint(1,40)}",
            "total_seats": 180,
            "available_seats": rng.randint(0, 180),
            "ticket_price": float(rng.randint(150, 1200) if "INTL" in dep or "INTL" in dst else rng.randint(50, 300)),
            "status": status_choice
        })
    return flights

MOCK_FLIGHTS = _generate_enhanced_flights(60) # Generate 60 for richness

# ── Mock Seat Data ──────────────────────────────────────────────────────────
def get_mock_seat_map(flight_id: int):
    reserved = []
    rng = random.Random(flight_id)
    # Different aircraft sizes could be simulated here
    for r in range(1, 31):
        for c in ["A", "B", "C", "D", "E", "F"]:
            if rng.random() < 0.4: # Slightly higher occupancy for realism
                reserved.append(f"{r}{c}")
    return reserved
