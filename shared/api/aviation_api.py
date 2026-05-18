"""
shared/api/aviation_api.py
--------------------------
Core Aviation Data API.
Handles fetching live flight information and seat status.
"""
from __future__ import annotations
from shared.api.mock_api import MOCK_FLIGHTS, get_mock_seat_map

def fetch_live_flights(departure: str = None, destination: str = None) -> list[dict]:
    """
    Simulates fetching live flights from a global distribution system.
    Returns a list of flight payloads.
    """
    results = MOCK_FLIGHTS
    
    if departure:
        results = [f for f in results if f["departure"].upper() == departure.upper()]
    
    if destination:
        results = [f for f in results if f["destination"].upper() == destination.upper()]
        
    return results

def get_seat_status(flight_id: int) -> dict:
    """
    Returns the current availability status of all seats for a given flight.
    Payload includes reserved vs available counts and specific seat labels.
    """
    reserved_labels = get_mock_seat_map(flight_id)
    total_capacity = 180 # Standard for our mock
    
    return {
        "flight_id": flight_id,
        "total_capacity": total_capacity,
        "reserved_count": len(reserved_labels),
        "available_count": total_capacity - len(reserved_labels),
        "reserved_seats": reserved_labels
    }
